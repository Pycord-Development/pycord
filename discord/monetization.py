"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-present Pycord Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import EntitlementType, SKUType, SubscriptionStatus, try_enum
from .flags import SKUFlags
from .iterators import SubscriptionIterator
from .mixins import Hashable
from .utils import MISSING
from .utils.private import get_as_snowflake, parse_time

if TYPE_CHECKING:
    from datetime import datetime

    from .abc import Snowflake, SnowflakeTime
    from .state import ConnectionState
    from .types.monetization import SKU as SKUPayload
    from .types.monetization import Entitlement as EntitlementPayload
    from .types.monetization import Subscription as SubscriptionPayload


__all__ = (
    "SKU",
    "Entitlement",
    "Subscription",
)


class SKU(Hashable):
    """Represents a Discord SKU (stock-keeping unit).

    .. versionadded:: 2.5

    Attributes
    ----------
    id: :class:`int`
        The SKU's ID.
    type: :class:`SKUType`
        The type of SKU.
    application_id: :class:`int`
        The ID of the application this SKU belongs to.
    name: :class:`str`
        The name of the SKU.
    slug: :class:`str`
        The SKU's slug.
    flags: :class:`SKUFlags`
        The SKU's flags.
    """

    __slots__ = (
        "_state",
        "id",
        "type",
        "application_id",
        "name",
        "slug",
        "flags",
    )

    def __init__(self, *, state: ConnectionState, data: SKUPayload) -> None:
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self.type: SKUType = try_enum(SKUType, data["type"])
        self.application_id: int = int(data["application_id"])
        self.name: str = data["name"]
        self.slug: str = data["slug"]
        self.flags: SKUFlags = SKUFlags._from_value(data["flags"])

    def __repr__(self) -> str:
        return (
            f"<SKU id={self.id} name={self.name!r} application_id={self.application_id} "
            f"slug={self.slug!r} flags={self.flags!r}>"
        )

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    @property
    def url(self) -> str:
        """:class:`str`: Returns the URL for the SKU."""
        return f"https://discord.com/application-directory/{self.application_id}/store/{self.id}"

    def fetch_subscriptions(
        self,
        user: Snowflake,  # user is required because this is a bot, we are not using oauth2
        *,
        before: SnowflakeTime | None = None,
        after: SnowflakeTime | None = None,
        limit: int | None = 100,
    ) -> SubscriptionIterator:
        """Returns an :class:`.AsyncIterator` that enables fetching the SKU's subscriptions.

        .. versionadded:: 2.7

        Parameters
        ----------
        user: :class:`.abc.Snowflake`
            The user for which to retrieve subscriptions.
        before: :class:`.abc.Snowflake` | :class:`datetime.datetime` | None
            Retrieves subscriptions before this date or object.
            If a datetime is provided, it is recommended to use a UTC-aware datetime.
            If the datetime is naive, it is assumed to be local time.
        after: :class:`.abc.Snowflake` | :class:`datetime.datetime` | None
            Retrieve subscriptions after this date or object.
            If a datetime is provided, it is recommended to use a UTC-aware datetime.
            If the datetime is naive, it is assumed to be local time.
        limit: :class:`int` | None
            The number of subscriptions to retrieve. If ``None``, retrieves all subscriptions.

        Yields
        ------
        :class:`Subscription`
            A subscription that the user has for this SKU.

        Raises
        ------
        :exc:`HTTPException`
            Getting the subscriptions failed.

        Examples
        --------

        Usage ::

            async for subscription in sku.fetch_subscriptions(discord.Object(id=123456789)):
                print(subscription.status)

        Flattening into a list ::

            subscriptions = await sku.fetch_subscriptions(discord.Object(id=123456789)).flatten()
            # subscriptions is now a list of Subscription...

        All parameters except for ``user`` are optional.
        """
        return SubscriptionIterator(
            self._state,
            self.id,
            user_id=user.id,
            before=before,
            after=after,
            limit=limit,
        )


class Entitlement(Hashable):
    """Represents a Discord entitlement.

    .. versionadded:: 2.5

    .. note::

        As of October 1, 2024, entitlements that have been purchased will have ``ends_at`` set to ``None``
        unless the parent :class:`Subscription` has been cancelled.

        `See the Discord changelog. <https://discord.com/developers/docs/change-log#premium-apps-entitlement-migration-and-new-subscription-api>`_

    Attributes
    ----------
    id: :class:`int`
        The entitlement's ID.
    sku_id: :class:`int`
        The ID of the SKU this entitlement is for.
    application_id: :class:`int`
        The ID of the application this entitlement belongs to.
    user_id: Union[:class:`int`, :class:`MISSING`]
        The ID of the user that owns this entitlement.
    type: :class:`EntitlementType`
        The type of entitlement.
    deleted: :class:`bool`
        Whether the entitlement has been deleted.
    starts_at: Union[:class:`datetime.datetime`, :class:`MISSING`]
        When the entitlement starts.
    ends_at: Union[:class:`datetime.datetime`, :class:`MISSING`]
        When the entitlement expires.
    guild_id: Union[:class:`int`, :class:`MISSING`]
        The ID of the guild that owns this entitlement.
    consumed: :class:`bool`
        Whether or not this entitlement has been consumed.
        This will always be ``False`` for entitlements that are not
        from an SKU of type :attr:`SKUType.consumable`.
    """

    __slots__ = (
        "_state",
        "id",
        "sku_id",
        "application_id",
        "user_id",
        "type",
        "deleted",
        "starts_at",
        "ends_at",
        "guild_id",
        "consumed",
    )

    def __init__(self, *, data: EntitlementPayload, state: ConnectionState) -> None:
        self._state = state
        self.id: int = int(data["id"])
        self.sku_id: int = int(data["sku_id"])
        self.application_id: int = int(data["application_id"])
        self.user_id: int | MISSING = get_as_snowflake(data, "user_id") or MISSING
        self.type: EntitlementType = try_enum(EntitlementType, data["type"])
        self.deleted: bool = data["deleted"]
        self.starts_at: datetime | MISSING = parse_time(data.get("starts_at")) or MISSING
        self.ends_at: datetime | MISSING | None = parse_time(ea) if (ea := data.get("ends_at")) is not None else MISSING
        self.guild_id: int | MISSING = get_as_snowflake(data, "guild_id") or MISSING
        self.consumed: bool = data.get("consumed", False)

    def __repr__(self) -> str:
        return (
            f"<Entitlement id={self.id} sku_id={self.sku_id} application_id={self.application_id} "
            f"user_id={self.user_id} type={self.type} deleted={self.deleted} "
            f"starts_at={self.starts_at} ends_at={self.ends_at} guild_id={self.guild_id} consumed={self.consumed}>"
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    async def consume(self) -> None:
        """|coro|

        Consumes this entitlement.

        This can only be done on entitlements from an SKU of type :attr:`SKUType.consumable`.

        Raises
        ------
        HTTPException
            Consuming the entitlement failed.
        """
        await self._state.http.consume_entitlement(self._state.application_id, self.id)
        self.consumed = True

    async def delete(self) -> None:
        """|coro|

        Deletes a test entitlement.

        A test entitlement is an entitlement that was created using :meth:`Guild.create_test_entitlement` or :meth:`User.create_test_entitlement`.

        Raises
        ------
        HTTPException
            Deleting the entitlement failed.
        """
        await self._state.http.delete_test_entitlement(self.application_id, self.id)


class Subscription(Hashable):
    """Represents a user making recurring payments for one or more SKUs.

    Successful payments grant the user access to entitlements associated with the SKU.

    .. versionadded:: 2.7

    Attributes
    ----------
    id: :class:`int`
        The subscription's ID.
    user_id: :class:`int`
        The ID of the user that owns this subscription.
    sku_ids: List[:class:`int`]
        The IDs of the SKUs this subscription is for.
    entitlement_ids: List[:class:`int`]
        The IDs of the entitlements this subscription is for.
    renewal_sku_ids: List[:class:`int`]
        The IDs of the SKUs that the buyer will be subscribed to at renewal.
    current_period_start: :class:`datetime.datetime`
        The start of the current subscription period.
    current_period_end: :class:`datetime.datetime`
        The end of the current subscription period.
    status: :class:`SubscriptionStatus`
        The status of the subscription.
    canceled_at: :class:`datetime.datetime` | ``None``
        When the subscription was canceled.
    """

    __slots__ = (
        "_state",
        "id",
        "user_id",
        "sku_ids",
        "entitlement_ids",
        "renewal_sku_ids",
        "current_period_start",
        "current_period_end",
        "status",
        "canceled_at",
        "country",
    )

    def __init__(self, *, state: ConnectionState, data: SubscriptionPayload) -> None:
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self.user_id: int = int(data["user_id"])
        self.sku_ids: list[int] = list(map(int, data["sku_ids"]))
        self.entitlement_ids: list[int] = list(map(int, data["entitlement_ids"]))
        self.renewal_sku_ids: list[int] = list(map(int, data["renewal_sku_ids"] or []))
        self.current_period_start: datetime = parse_time(data["current_period_start"])
        self.current_period_end: datetime = parse_time(data["current_period_end"])
        self.status: SubscriptionStatus = try_enum(SubscriptionStatus, data["status"])
        self.canceled_at: datetime | None = parse_time(data.get("canceled_at"))
        self.country: str | None = data.get("country")  # Not documented, it is only available with oauth2, not bots

    def __repr__(self) -> str:
        return f"<Subscription id={self.id} user_id={self.user_id} status={self.status}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    @property
    def user(self):
        """Optional[:class:`User`]: The user that owns this subscription."""
        return self._state.get_user(self.user_id)
