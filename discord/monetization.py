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

from .enums import EntitlementType, SKUType, try_enum
from .flags import SKUFlags
from .mixins import Hashable
from .utils import MISSING, _get_as_snowflake, parse_time

if TYPE_CHECKING:
    from datetime import datetime

    from .state import ConnectionState
    from .types.monetization import SKU as SKUPayload
    from .types.monetization import Entitlement as EntitlementPayload


__all__ = (
    "SKU",
    "Entitlement",
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
        "id",
        "type",
        "application_id",
        "name",
        "slug",
        "flags",
    )

    def __init__(self, *, data: SKUPayload) -> None:
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


class Entitlement(Hashable):
    """Represents a Discord entitlement.

    .. versionadded:: 2.5

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
        of type :attr:`EntitlementType.consumable`.
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
        self.user_id: int | MISSING = _get_as_snowflake(data, "user_id") or MISSING
        self.type: EntitlementType = try_enum(EntitlementType, data["type"])
        self.deleted: bool = data["deleted"]
        self.starts_at: datetime | MISSING = (
            parse_time(data.get("starts_at")) or MISSING
        )
        self.ends_at: datetime | MISSING = parse_time(data.get("ends_at")) or MISSING
        self.guild_id: int | MISSING = _get_as_snowflake(data, "guild_id") or MISSING
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

        This can only be done on entitlements of type :attr:`EntitlementType.consumable`.

        Raises
        ------
        TypeError
            The entitlement is not consumable.
        HTTPException
            Consuming the entitlement failed.
        """
        if self.type is not EntitlementType.consumable:
            raise TypeError("Cannot consume non-consumable entitlement")

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
