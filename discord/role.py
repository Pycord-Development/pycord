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

from enum import IntEnum
from typing import TYPE_CHECKING, Any, TypeVar

from .asset import Asset
from .colour import Colour
from .errors import InvalidArgument
from .flags import RoleFlags
from .mixins import Hashable
from .permissions import Permissions
from .utils import (
    MISSING,
    _bytes_to_base64_data,
    cached_slot_property,
    deprecated,
    snowflake_time,
)

__all__ = (
    "RoleTags",
    "Role",
)

if TYPE_CHECKING:
    import datetime

    from .guild import Guild
    from .member import Member
    from .state import ConnectionState
    from .types.guild import RolePositionUpdate
    from .types.role import Role as RolePayload
    from .types.role import RoleTags as RoleTagPayload


def _parse_tag_bool(data: RoleTagPayload, key: str) -> bool | None:
    """Parse a boolean from a role tag payload.

    None is returned if the key is not present.
    True is returned if the key is present and the value is None.
    False is returned if the key is present and the value is not None.

    Parameters
    ----------
    data: :class:`RoleTagPayload`
        The role tag payload to parse from.
    key: :class:`str`
        The key to parse from.

    Returns
    -------
    :class:`bool` | :class:`None`
        The parsed boolean value or None if the key is not present.
    """
    try:
        # if it is False, False != None -> False
        # if it is None, None == None -> True
        return data[key] is None
    except KeyError:
        # if the key is not present, None
        return None


def _parse_tag_int(data: RoleTagPayload, key: str) -> int | None:
    """Parse an integer from a role tag payload.

    An integer is returned if the key is present and the value is an integer string.
    None is returned if the key is not present or the value is not an integer string.

    Parameters
    ----------
    data: :class:`RoleTagPayload`
        The role tag payload to parse from.
    key: :class:`str`
        The key to parse from.

    Returns
    -------
    :class:`int` | :class:`None`
        The parsed integer value or None if the key is not present or the value is not an integer string.
    """
    try:
        return int(data[key])  # pyright: ignore[reportUnknownArgumentType]
    except (KeyError, ValueError):
        # key error means it's not there
        # value error means it's not an number string (None or "")
        return None


class RoleType(IntEnum):
    """Represents the type of role.

    This is NOT provided by discord but is rather computed by pycord based on the role tags.

    .. versionadded:: 2.7

    Attributes
    ----------
    NORMAL: :class:`int`
        The role is a normal role.
    APPLICATION: :class:`int`
        The role is an application (bot) role.
    BOOSTER: :class:`int`
        The role is a guild's booster role.
    GUILD_PRODUCT: :class:`int`
        The role is a guild product role.
    PREMIUM_SUBSCRIPTION_BASE: :class:`int`
        The role is a base subscription role. This is not possible to determine currently, will be INTEGRATION if it's a base subscription.
    PREMIUM_SUBSCRIPTION_TIER: :class:`int`
        The role is a subscription role.
    DRAFT_PREMIUM_SUBSCRIPTION_TIER: :class:`int`
        The role is a draft subscription role.
    INTEGRATION: :class:`int`
        The role is an integration role, such as Twitch or YouTube, or a base subscription role.
    CONNECTION: :class:`int`
        The role is a guild connections role.
    UNKNOWN: :class:`int`
        The role type is unknown.
    """

    NORMAL = 0
    APPLICATION = 1
    BOOSTER = 2
    GUILD_PRODUCT = 3
    PREMIUM_SUBSCRIPTION_BASE = 4  # Not possible to determine currently, will be INTEGRATION if it's a base subscription
    PREMIUM_SUBSCRIPTION_TIER = 5
    DRAFT_PREMIUM_SUBSCRIPTION_TIER = 6
    INTEGRATION = 7
    CONNECTION = 8
    UNKNOWN = 9


class RoleTags:
    """Represents tags on a role.

    A role tag is a piece of extra information attached to a managed role
    that gives it context for the reason the role is managed.

    Role tags are a fairly complex topic, since it's usually hard to determine which role tag combination represents which role type.
    In order to make your life easier, pycord provides a :attr:`RoleTags.type` attribute that attempts to determine the role type based on the role tags. It's value is not provided by discord but is rather computed by pycord based on the role tags.
    If you find an issue, please open an issue on `GitHub <https://github.com/Pycord-Development/pycord/issues/new?template=bug_report.yml>`_.
    Read `this <https://lulalaby.notion.site/Special-Roles-Documentation-17411d3839e680abbb1eff63c51bd7a7?pvs=4>`_ if you need detailed information about how role tags work.

    .. versionadded:: 1.6
    .. versionchanged:: 2.7
        The type of the role is now determined by the :attr:`RoleTags.type` attribute.

    Attributes
    ----------
    bot_id: Optional[:class:`int`]
        The bot's user ID that manages this role.
    integration_id: Optional[:class:`int`]
        The integration ID that manages the role.
    subscription_listing_id: Optional[:class:`int`]
        The subscription SKU and listing ID of the role.

        .. versionadded:: 2.7
    """

    __slots__ = (
        "integration_id",
        "subscription_listing_id",
        "_premium_subscriber",
        "_available_for_purchase",
        "_guild_connections",
        "_is_guild_product_role",
        "bot_id",
        "_data",
        "_type",
    )

    def __init__(self, data: RoleTagPayload):
        self._data: RoleTagPayload = data
        self.integration_id: int | None = _parse_tag_int(data, "integration_id")
        self.subscription_listing_id: int | None = _parse_tag_int(
            data, "subscription_listing_id"
        )
        self.bot_id: int | None = _parse_tag_int(data, "bot_id")
        self._guild_connections: bool | None = _parse_tag_bool(
            data, "guild_connections"
        )
        self._premium_subscriber: bool | None = _parse_tag_bool(
            data, "premium_subscriber"
        )
        self._available_for_purchase: bool | None = _parse_tag_bool(
            data, "available_for_purchase"
        )
        # here discord did things in a normal and logical way for once
        self._is_guild_product_role: bool | None = data.get("is_guild_product_role")

    @cached_slot_property("_type")
    def type(self) -> RoleType:
        """Determine the role type based on tag flags."""
        # Bot role
        if self.bot_id is not None:
            return RoleType.APPLICATION

        # Role connection
        if self._guild_connections is True:
            return RoleType.CONNECTION

        # Paid roles
        if self._is_guild_product_role is True:
            return RoleType.GUILD_PRODUCT

        # Booster role
        if self._premium_subscriber is True:
            return RoleType.BOOSTER

        # subscription roles
        if (
            self.integration_id is not None
            and self._premium_subscriber is None
            and self.subscription_listing_id is not None
        ):
            if self._available_for_purchase is True:
                return RoleType.PREMIUM_SUBSCRIPTION_TIER
            return RoleType.DRAFT_PREMIUM_SUBSCRIPTION_TIER

        # integration role (Twitch/YouTube)
        if self.integration_id is not None:
            return RoleType.INTEGRATION

        # Seeing how messed up this is it wouldn't be a surprise if this happened
        return RoleType.UNKNOWN

    @deprecated("RoleTags.type", "2.7")
    def is_bot_managed(self) -> bool:
        """Whether the role is associated with a bot."""
        return self.bot_id is not None

    @deprecated("RoleTags.type", "2.7")
    def is_premium_subscriber(self) -> bool:
        """Whether the role is the premium subscriber, AKA "boost", role for the guild."""
        return self._premium_subscriber is None

    @deprecated("RoleTags.type", "2.7")
    def is_integration(self) -> bool:
        """Whether the guild manages the role through some form of
        integrations such as Twitch or through guild subscriptions.
        """
        return self.integration_id is not None

    @deprecated("RoleTags.type", "2.7")
    def is_available_for_purchase(self) -> bool:
        """Whether the role is available for purchase."""
        return self._available_for_purchase is True

    @deprecated("RoleTags.type", "2.7")
    def is_guild_connections_role(self) -> bool:
        """Whether the role is a guild connections role."""
        return self._guild_connections is True

    def __repr__(self) -> str:
        return (
            f"<RoleTags bot_id={self.bot_id} integration_id={self.integration_id} "
            + f"subscription_listing_id={self.subscription_listing_id} "
            + f"type={self.type!r}>"
        )


R = TypeVar("R", bound="Role")


class Role(Hashable):
    """Represents a Discord role in a :class:`Guild`.

    .. container:: operations

        .. describe:: x == y

            Checks if two roles are equal.

        .. describe:: x != y

            Checks if two roles are not equal.

        .. describe:: x > y

            Checks if a role is higher than another in the hierarchy.

        .. describe:: x < y

            Checks if a role is lower than another in the hierarchy.

        .. describe:: x >= y

            Checks if a role is higher or equal to another in the hierarchy.

        .. describe:: x <= y

            Checks if a role is lower or equal to another in the hierarchy.

        .. describe:: hash(x)

            Return the role's hash.

        .. describe:: str(x)

            Returns the role's name.

    Attributes
    ----------
    id: :class:`int`
        The ID for the role.
    name: :class:`str`
        The name of the role.
    guild: :class:`Guild`
        The guild the role belongs to.
    hoist: :class:`bool`
         Indicates if the role will be displayed separately from other members.
    position: :class:`int`
        The position of the role. This number is usually positive. The bottom
        role has a position of 0.

        .. warning::

            Multiple roles can have the same position number. As a consequence
            of this, comparing via role position is prone to subtle bugs if
            checking for role hierarchy. The recommended and correct way to
            compare for roles in the hierarchy is using the comparison
            operators on the role objects themselves.

    managed: :class:`bool`
        Indicates if the role is managed by the guild.
        This is true if any of :meth:`Role.is_integration`, :meth:`Role.is_premium_subscriber`,
        :meth:`Role.is_bot_managed` or :meth:`Role.is_guild_connections_role`
        is ``True``.
    mentionable: :class:`bool`
        Indicates if the role can be mentioned by users.
    tags: Optional[:class:`RoleTags`]
        The role tags associated with this role. Use the tags to determine additional information about the role,
        like if it's a bot role, a booster role, etc...
    unicode_emoji: Optional[:class:`str`]
        The role's unicode emoji.
        Only available to guilds that contain ``ROLE_ICONS`` in :attr:`Guild.features`.

        .. versionadded:: 2.0

    flags: :class:`RoleFlags`
        Extra attributes of the role.

        .. versionadded:: 2.6
    """

    __slots__ = (
        "id",
        "name",
        "_permissions",
        "_colour",
        "position",
        "managed",
        "mentionable",
        "hoist",
        "guild",
        "tags",
        "unicode_emoji",
        "_icon",
        "_state",
        "flags",
    )

    def __init__(self, *, guild: Guild, state: ConnectionState, data: RolePayload):
        self.guild: Guild = guild
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self._update(data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Role id={self.id} name={self.name!r}>"

    def __lt__(self: R, other: R) -> bool:
        if not isinstance(other, Role) or not isinstance(self, Role):
            return NotImplemented

        if self.guild != other.guild:
            raise RuntimeError("cannot compare roles from two different guilds.")

        # the @everyone role is always the lowest role in hierarchy
        guild_id = self.guild.id
        if self.id == guild_id:
            # everyone_role < everyone_role -> False
            return other.id != guild_id

        if self.position < other.position:
            return True

        if self.position == other.position:
            return int(self.id) > int(other.id)

        return False

    def __le__(self: R, other: R) -> bool:
        r = Role.__lt__(other, self)
        if r is NotImplemented:
            return NotImplemented
        return not r

    def __gt__(self: R, other: R) -> bool:
        return Role.__lt__(other, self)

    def __ge__(self: R, other: R) -> bool:
        r = Role.__lt__(self, other)
        if r is NotImplemented:
            return NotImplemented
        return not r

    def _update(self, data: RolePayload):
        self.name: str = data["name"]
        self._permissions: int = int(data.get("permissions", 0))
        self.position: int = data.get("position", 0)
        self._colour: int = data.get("color", 0)
        self.hoist: bool = data.get("hoist", False)
        self.managed: bool = data.get("managed", False)
        self.mentionable: bool = data.get("mentionable", False)
        self._icon: str | None = data.get("icon")
        self.unicode_emoji: str | None = data.get("unicode_emoji")
        self.flags: RoleFlags = RoleFlags._from_value(data.get("flags", 0))
        self.tags: RoleTags | None

        try:
            self.tags = RoleTags(data["tags"])
        except KeyError:
            self.tags = None

    def is_default(self) -> bool:
        """Checks if the role is the default role."""
        return self.guild.id == self.id

    @deprecated("Role.type", "2.7")
    def is_bot_managed(self) -> bool:
        """Whether the role is associated with a bot.

        .. versionadded:: 1.6
        """
        return self.tags is not None and self.tags.is_bot_managed()

    @deprecated("Role.type", "2.7")
    def is_premium_subscriber(self) -> bool:
        """Whether the role is the premium subscriber, AKA "boost", role for the guild.

        .. versionadded:: 1.6
        """
        return self.tags is not None and self.tags.is_premium_subscriber()

    @deprecated("Role.type", "2.7")
    def is_integration(self) -> bool:
        """Whether the guild manages the role through some form of
        integrations such as Twitch or through guild subscriptions.

        .. versionadded:: 1.6
        """
        return self.tags is not None and self.tags.is_integration()

    def is_assignable(self) -> bool:
        """Whether the role is able to be assigned or removed by the bot.

        .. versionadded:: 2.0
        """
        me = self.guild.me
        return (
            not self.is_default()
            and not self.managed
            and (me.top_role > self or me.id == self.guild.owner_id)
        )

    @deprecated("Role.type", "2.7")
    def is_available_for_purchase(self) -> bool:
        """Whether the role is available for purchase.

        Returns ``True`` if the role is available for purchase, and
        ``False`` if it is not available for purchase or if the
        role is not linked to a guild subscription.

        .. versionadded:: 2.7
        """
        return self.tags is not None and self.tags.is_available_for_purchase()

    @deprecated("Role.type", "2.7")
    def is_guild_connections_role(self) -> bool:
        """Whether the role is a guild connections role.

        .. versionadded:: 2.7
        """
        return self.tags is not None and self.tags.is_guild_connections_role()

    @property
    def permissions(self) -> Permissions:
        """Returns the role's permissions."""
        return Permissions(self._permissions)

    @property
    def colour(self) -> Colour:
        """Returns the role colour. An alias exists under ``color``."""
        return Colour(self._colour)

    @property
    def color(self) -> Colour:
        """Returns the role color. An alias exists under ``colour``."""
        return self.colour

    @property
    def created_at(self) -> datetime.datetime:
        """Returns the role's creation time in UTC."""
        return snowflake_time(self.id)

    @property
    def mention(self) -> str:
        """Returns a string that allows you to mention a role."""
        return f"<@&{self.id}>"

    @property
    def members(self) -> list[Member]:
        """Returns all the members with this role."""
        all_members = self.guild.members
        if self.is_default():
            return all_members

        role_id = self.id
        return [member for member in all_members if member._roles.has(role_id)]

    @property
    def icon(self) -> Asset | None:
        """Returns the role's icon asset, if available.

        .. versionadded:: 2.0
        """
        if self._icon is None:
            return None

        return Asset._from_icon(self._state, self.id, self._icon, "role")

    @property
    def type(self) -> RoleType:
        """The type of the role.

        .. versionadded:: 2.7
        """
        return self.tags.type if self.tags is not None else RoleType.NORMAL

    async def _move(self, position: int, reason: str | None) -> None:
        if position <= 0:
            raise InvalidArgument("Cannot move role to position 0 or below")

        if self.is_default():
            raise InvalidArgument("Cannot move default role")

        if self.position == position:
            return  # Save discord the extra request.

        http = self._state.http

        change_range = range(
            min(self.position, position), max(self.position, position) + 1
        )
        roles = [
            r.id
            for r in self.guild.roles[1:]
            if r.position in change_range and r.id != self.id
        ]

        if self.position > position:
            roles.insert(0, self.id)
        else:
            roles.append(self.id)

        payload: list[RolePositionUpdate] = [
            {"id": z[0], "position": z[1]} for z in zip(roles, change_range)
        ]
        await http.move_role_position(self.guild.id, payload, reason=reason)

    async def edit(
        self,
        *,
        name: str = MISSING,
        permissions: Permissions = MISSING,
        colour: Colour | int = MISSING,
        color: Colour | int = MISSING,
        hoist: bool = MISSING,
        mentionable: bool = MISSING,
        position: int = MISSING,
        reason: str | None = MISSING,
        icon: bytes | None = MISSING,
        unicode_emoji: str | None = MISSING,
    ) -> Role | None:
        """|coro|

        Edits the role.

        You must have the :attr:`~Permissions.manage_roles` permission to
        use this.

        All fields are optional.

        .. versionchanged:: 1.4
            Can now pass ``int`` to ``colour`` keyword-only parameter.

        .. versionchanged:: 2.0
            Edits are no longer in-place, the newly edited role is returned instead.
            Added ``icon`` and ``unicode_emoji``.

        Parameters
        ----------
        name: :class:`str`
            The new role name to change to.
        permissions: :class:`Permissions`
            The new permissions to change to.
        colour: Union[:class:`Colour`, :class:`int`]
            The new colour to change to. (aliased to color as well)
        hoist: :class:`bool`
            Indicates if the role should be shown separately in the member list.
        mentionable: :class:`bool`
            Indicates if the role should be mentionable by others.
        position: :class:`int`
            The new role's position. This must be below your top role's
            position, or it will fail.
        reason: Optional[:class:`str`]
            The reason for editing this role. Shows up on the audit log.
        icon: Optional[:class:`bytes`]
            A :term:`py:bytes-like object` representing the icon. Only PNG/JPEG/WebP is supported.
            If this argument is passed, ``unicode_emoji`` is set to None.
            Only available to guilds that contain ``ROLE_ICONS`` in :attr:`Guild.features`.
            Could be ``None`` to denote removal of the icon.
        unicode_emoji: Optional[:class:`str`]
            The role's unicode emoji. If this argument is passed, ``icon`` is set to None.
            Only available to guilds that contain ``ROLE_ICONS`` in :attr:`Guild.features`.

        Returns
        -------
        :class:`Role`
            The newly edited role.

        Raises
        ------
        Forbidden
            You do not have permissions to change the role.
        HTTPException
            Editing the role failed.
        InvalidArgument
            An invalid position was given or the default
            role was asked to be moved.
        """
        if position is not MISSING:
            await self._move(position, reason=reason)

        payload: dict[str, Any] = {}
        if color is not MISSING:
            colour = color

        if colour is not MISSING:
            payload["color"] = colour if isinstance(colour, int) else colour.value
        if name is not MISSING:
            payload["name"] = name

        if permissions is not MISSING:
            payload["permissions"] = permissions.value

        if hoist is not MISSING:
            payload["hoist"] = hoist

        if mentionable is not MISSING:
            payload["mentionable"] = mentionable

        if icon is not MISSING:
            if icon is None:
                payload["icon"] = None
            else:
                payload["icon"] = _bytes_to_base64_data(icon)
                payload["unicode_emoji"] = None

        if unicode_emoji is not MISSING:
            payload["unicode_emoji"] = unicode_emoji
            payload["icon"] = None

        data = await self._state.http.edit_role(
            self.guild.id, self.id, reason=reason, **payload
        )
        return Role(guild=self.guild, data=data, state=self._state)

    async def delete(self, *, reason: str | None = None) -> None:
        """|coro|

        Deletes the role.

        You must have the :attr:`~Permissions.manage_roles` permission to
        use this.

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason for deleting this role. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have permissions to delete the role.
        HTTPException
            Deleting the role failed.
        """

        await self._state.http.delete_role(self.guild.id, self.id, reason=reason)
