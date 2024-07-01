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

from typing import TYPE_CHECKING, Any, TypeVar

import discord.abc

from .asset import Asset
from .colour import Colour
from .flags import PublicUserFlags
from .iterators import EntitlementIterator
from .monetization import Entitlement
from .utils import MISSING, _bytes_to_base64_data, snowflake_time

if TYPE_CHECKING:
    from datetime import datetime

    from .abc import Snowflake, SnowflakeTime
    from .channel import DMChannel
    from .guild import Guild
    from .message import Message
    from .state import ConnectionState
    from .types.channel import DMChannel as DMChannelPayload
    from .types.user import PartialUser as PartialUserPayload
    from .types.user import User as UserPayload


__all__ = (
    "User",
    "ClientUser",
)

BU = TypeVar("BU", bound="BaseUser")


class _UserTag:
    __slots__ = ()
    id: int


class BaseUser(_UserTag):
    __slots__ = (
        "name",
        "id",
        "discriminator",
        "global_name",
        "_avatar",
        "_banner",
        "_accent_colour",
        "bot",
        "system",
        "_public_flags",
        "_avatar_decoration",
        "_state",
    )

    if TYPE_CHECKING:
        name: str
        id: int
        discriminator: str
        global_name: str | None
        bot: bool
        system: bool
        _state: ConnectionState
        _avatar: str | None
        _banner: str | None
        _accent_colour: int | None
        _avatar_decoration: dict | None
        _public_flags: int

    def __init__(
        self, *, state: ConnectionState, data: UserPayload | PartialUserPayload
    ) -> None:
        self._state = state
        self._update(data)

    def __repr__(self) -> str:
        if self.is_migrated:
            if self.global_name is not None:
                return (
                    "<BaseUser"
                    f" id={self.id} username={self.name!r} global_name={self.global_name!r}"
                    f" bot={self.bot} system={self.system}>"
                )
            return (
                "<BaseUser"
                f" id={self.id} username={self.name!r}"
                f" bot={self.bot} system={self.system}>"
            )
        return (
            "<BaseUser"
            f" id={self.id} name={self.name!r} discriminator={self.discriminator!r}"
            f" bot={self.bot} system={self.system}>"
        )

    def __str__(self) -> str:
        return (
            f"{self.name}#{self.discriminator}"
            if not self.is_migrated
            else (
                f"{self.name} ({self.global_name})"
                if self.global_name is not None
                else self.name
            )
        )

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, _UserTag) and other.id == self.id

    def __hash__(self) -> int:
        return self.id >> 22

    def _update(self, data: UserPayload) -> None:
        self.name = data["username"]
        self.id = int(data["id"])
        self.discriminator = data["discriminator"]
        self.global_name = data.get("global_name", None) or None
        self._avatar = data["avatar"]
        self._banner = data.get("banner", None)
        self._accent_colour = data.get("accent_color", None)
        self._avatar_decoration = data.get("avatar_decoration_data", None)
        self._public_flags = data.get("public_flags", 0)
        self.bot = data.get("bot", False)
        self.system = data.get("system", False)

    @classmethod
    def _copy(cls: type[BU], user: BU) -> BU:
        self = cls.__new__(cls)  # bypass __init__

        self.name = user.name
        self.id = user.id
        self.discriminator = user.discriminator
        self.global_name = user.global_name
        self._avatar = user._avatar
        self._banner = user._banner
        self._accent_colour = user._accent_colour
        self._avatar_decoration = user._avatar_decoration
        self.bot = user.bot
        self._state = user._state
        self._public_flags = user._public_flags

        return self

    def _to_minimal_user_json(self) -> dict[str, Any]:
        return {
            "username": self.name,
            "id": self.id,
            "avatar": self._avatar,
            "discriminator": self.discriminator,
            "global_name": self.global_name,
            "bot": self.bot,
        }

    @property
    def jump_url(self) -> str:
        """Returns a URL that allows the client to jump to the user.

        .. versionadded:: 2.0
        """
        return f"https://discord.com/users/{self.id}"

    @property
    def public_flags(self) -> PublicUserFlags:
        """The publicly available flags the user has."""
        return PublicUserFlags._from_value(self._public_flags)

    @property
    def avatar(self) -> Asset | None:
        """Returns an :class:`Asset` for the avatar the user has.

        If the user does not have a traditional avatar, ``None`` is returned.
        If you want the avatar that a user has displayed, consider :attr:`display_avatar`.
        """
        if self._avatar is not None:
            return Asset._from_avatar(self._state, self.id, self._avatar)
        return None

    @property
    def default_avatar(self) -> Asset:
        """Returns the default avatar for a given user.
        This is calculated by the user's ID if they're on the new username system, otherwise their discriminator.
        """
        eq = (self.id >> 22) if self.is_migrated else int(self.discriminator)
        perc = 6 if self.is_migrated else 5
        return Asset._from_default_avatar(self._state, eq % perc)

    @property
    def display_avatar(self) -> Asset:
        """Returns the user's display avatar.

        For regular users this is just their default avatar or uploaded avatar.

        .. versionadded:: 2.0
        """
        return self.avatar or self.default_avatar

    @property
    def banner(self) -> Asset | None:
        """Returns the user's banner asset, if available.

        .. versionadded:: 2.0

        .. note::
            This information is only available via :meth:`Client.fetch_user`.
        """
        if self._banner is None:
            return None
        return Asset._from_user_banner(self._state, self.id, self._banner)

    @property
    def avatar_decoration(self) -> Asset | None:
        """Returns the user's avatar decoration, if available.

        .. versionadded:: 2.5
        """
        if self._avatar_decoration is None:
            return None
        return Asset._from_avatar_decoration(
            self._state, self.id, self._avatar_decoration.get("asset")
        )

    @property
    def accent_colour(self) -> Colour | None:
        """Returns the user's accent colour, if applicable.

        There is an alias for this named :attr:`accent_color`.

        .. versionadded:: 2.0

        .. note::

            This information is only available via :meth:`Client.fetch_user`.
        """
        if self._accent_colour is None:
            return None
        return Colour(self._accent_colour)

    @property
    def accent_color(self) -> Colour | None:
        """Returns the user's accent color, if applicable.

        There is an alias for this named :attr:`accent_colour`.

        .. versionadded:: 2.0

        .. note::

            This information is only available via :meth:`Client.fetch_user`.
        """
        return self.accent_colour

    @property
    def colour(self) -> Colour:
        """A property that returns a colour denoting the rendered colour
        for the user. This always returns :meth:`Colour.default`.

        There is an alias for this named :attr:`color`.
        """
        return Colour.default()

    @property
    def color(self) -> Colour:
        """A property that returns a color denoting the rendered color
        for the user. This always returns :meth:`Colour.default`.

        There is an alias for this named :attr:`colour`.
        """
        return self.colour

    @property
    def mention(self) -> str:
        """Returns a string that allows you to mention the given user."""
        return f"<@{self.id}>"

    @property
    def created_at(self) -> datetime:
        """Returns the user's creation time in UTC.

        This is when the user's Discord account was created.
        """
        return snowflake_time(self.id)

    @property
    def display_name(self) -> str:
        """Returns the user's display name.
        This will be their global name if set, otherwise their username.
        """
        return self.global_name or self.name

    def mentioned_in(self, message: Message) -> bool:
        """Checks if the user is mentioned in the specified message.

        Parameters
        ----------
        message: :class:`Message`
            The message to check if you're mentioned in.

        Returns
        -------
        :class:`bool`
            Indicates if the user is mentioned in the message.
        """

        if message.mention_everyone:
            return True

        return any(user.id == self.id for user in message.mentions)

    @property
    def is_migrated(self) -> bool:
        """Checks whether the user is already migrated to global name."""
        return self.discriminator == "0"


class ClientUser(BaseUser):
    """Represents your Discord user.

    .. container:: operations

        .. describe:: x == y

            Checks if two users are equal.

        .. describe:: x != y

            Checks if two users are not equal.

        .. describe:: hash(x)

            Return the user's hash.

        .. describe:: str(x)

            Returns the user's name with discriminator or global_name.

    Attributes
    ----------
    name: :class:`str`
        The user's username.
    id: :class:`int`
        The user's unique ID.
    discriminator: :class:`str`
        The user's discriminator. This is given when the username has conflicts.

        .. note::

            If the user has migrated to the new username system, this will always be 0.
    global_name: :class:`str`
        The user's global name.

        .. versionadded:: 2.5
    bot: :class:`bool`
        Specifies if the user is a bot account.
    system: :class:`bool`
        Specifies if the user is a system user (i.e. represents Discord officially).

        .. versionadded:: 1.3
    verified: :class:`bool`
        Specifies if the user's email is verified.
    locale: Optional[:class:`str`]
        The IETF language tag used to identify the language the user is using.
    mfa_enabled: :class:`bool`
        Specifies if the user has MFA turned on and working.
    """

    __slots__ = ("locale", "_flags", "verified", "mfa_enabled", "__weakref__")

    if TYPE_CHECKING:
        verified: bool
        locale: str | None
        mfa_enabled: bool
        _flags: int

    def __init__(self, *, state: ConnectionState, data: UserPayload) -> None:
        super().__init__(state=state, data=data)

    def __repr__(self) -> str:
        if self.is_migrated:
            if self.global_name is not None:
                return (
                    "<ClientUser"
                    f" id={self.id} username={self.name!r} global_name={self.global_name!r}"
                    f" bot={self.bot} verified={self.verified} mfa_enabled={self.mfa_enabled}>"
                )
            return (
                "<ClientUser"
                f" id={self.id} username={self.name!r}"
                f" bot={self.bot} verified={self.verified} mfa_enabled={self.mfa_enabled}>"
            )
        return (
            "<ClientUser"
            f" id={self.id} name={self.name!r} discriminator={self.discriminator!r}"
            f" bot={self.bot} verified={self.verified} mfa_enabled={self.mfa_enabled}>"
        )

    def _update(self, data: UserPayload) -> None:
        super()._update(data)
        # There's actually an Optional[str] phone field as well, but I won't use it
        self.verified = data.get("verified", False)
        self.locale = data.get("locale")
        self._flags = data.get("flags", 0)
        self.mfa_enabled = data.get("mfa_enabled", False)

    # TODO: Username might not be able to edit anymore.
    async def edit(
        self,
        *,
        username: str = MISSING,
        avatar: bytes = MISSING,
        banner: bytes = MISSING,
    ) -> ClientUser:
        """|coro|

        Edits the current profile of the client.

        .. note::

            To upload an avatar or banner, a :term:`py:bytes-like object` must be passed in that
            represents the image being uploaded. If this is done through a file
            then the file must be opened via ``open('some_filename', 'rb')`` and
            the :term:`py:bytes-like object` is given through the use of ``fp.read()``.

            The only image formats supported for uploading are JPEG, PNG, and GIF.

        .. versionchanged:: 2.0
            The edit is no longer in-place, instead the newly edited client user is returned.

        .. versionchanged:: 2.6
            The ``banner`` keyword-only parameter was added.

        Parameters
        ----------
        username: :class:`str`
            The new username you wish to change to.
        avatar: :class:`bytes`
            A :term:`py:bytes-like object` representing the image to upload.
            Could be ``None`` to denote no avatar.
        banner: :class:`bytes`
            A :term:`py:bytes-like object` representing the image to upload.
            Could be ``None`` to denote no banner.

        Returns
        -------
        :class:`ClientUser`
            The newly edited client user.

        Raises
        ------
        HTTPException
            Editing your profile failed.
        InvalidArgument
            Wrong image format passed for ``avatar`` or ``banner``.
        """
        payload: dict[str, Any] = {}
        if username is not MISSING:
            payload["username"] = username

        if avatar is None:
            payload["avatar"] = None
        elif avatar is not MISSING:
            payload["avatar"] = _bytes_to_base64_data(avatar)

        if banner is None:
            payload["banner"] = None
        elif banner is not MISSING:
            payload["banner"] = _bytes_to_base64_data(banner)

        data: UserPayload = await self._state.http.edit_profile(payload)
        return ClientUser(state=self._state, data=data)


class User(BaseUser, discord.abc.Messageable):
    """Represents a Discord user.

    .. container:: operations

        .. describe:: x == y

            Checks if two users are equal.

        .. describe:: x != y

            Checks if two users are not equal.

        .. describe:: hash(x)

            Return the user's hash.

        .. describe:: str(x)

            Returns the user's name with discriminator or global_name.

    Attributes
    ----------
    name: :class:`str`
        The user's username.
    id: :class:`int`
        The user's unique ID.
    discriminator: :class:`str`
        The user's discriminator. This is given when the username has conflicts.

        .. note::

            If the user has migrated to the new username system, this will always be "0".
    global_name: :class:`str`
        The user's global name.

        .. versionadded:: 2.5
    bot: :class:`bool`
        Specifies if the user is a bot account.
    system: :class:`bool`
        Specifies if the user is a system user (i.e. represents Discord officially).
    """

    __slots__ = ("_stored",)

    def __init__(self, *, state: ConnectionState, data: UserPayload) -> None:
        super().__init__(state=state, data=data)
        self._stored: bool = False

    def __repr__(self) -> str:
        if self.is_migrated:
            if self.global_name is not None:
                return (
                    "<User"
                    f" id={self.id} username={self.name!r} global_name={self.global_name!r} bot={self.bot}>"
                )
            return "<User" f" id={self.id} username={self.name!r} bot={self.bot}>"
        return (
            "<User"
            f" id={self.id} name={self.name!r} discriminator={self.discriminator!r} bot={self.bot}>"
        )

    def __del__(self) -> None:
        try:
            if self._stored:
                self._state.deref_user(self.id)
        except Exception:
            pass

    @classmethod
    def _copy(cls, user: User):
        self = super()._copy(user)
        self._stored = False
        return self

    async def _get_channel(self) -> DMChannel:
        ch = await self.create_dm()
        return ch

    @property
    def dm_channel(self) -> DMChannel | None:
        """Returns the channel associated with this user if it exists.

        If this returns ``None``, you can create a DM channel by calling the
        :meth:`create_dm` coroutine function.
        """
        return self._state._get_private_channel_by_user(self.id)

    @property
    def mutual_guilds(self) -> list[Guild]:
        """The guilds that the user shares with the client.

        .. note::

            This will only return mutual guilds within the client's internal cache.

        .. versionadded:: 1.7
        """
        return [
            guild for guild in self._state._guilds.values() if guild.get_member(self.id)
        ]

    async def create_dm(self) -> DMChannel:
        """|coro|

        Creates a :class:`DMChannel` with this user.

        This should be rarely called, as this is done transparently for most
        people.

        Returns
        -------
        :class:`.DMChannel`
            The channel that was created.
        """
        found = self.dm_channel
        if found is not None:
            return found

        state = self._state
        data: DMChannelPayload = await state.http.start_private_message(self.id)
        return state.add_dm_channel(data)

    async def create_test_entitlement(self, sku: discord.abc.Snowflake) -> Entitlement:
        """|coro|

        Creates a test entitlement for the user.

        Parameters
        ----------
        sku: :class:`Snowflake`
            The SKU to create a test entitlement for.

        Returns
        -------
        :class:`Entitlement`
            The created entitlement.
        """
        payload = {
            "sku_id": sku.id,
            "owner_id": self.id,
            "owner_type": 2,
        }
        data = await self._state.http.create_test_entitlement(self.id, payload)
        return Entitlement(data=data, state=self._state)

    def entitlements(
        self,
        skus: list[Snowflake] | None = None,
        before: SnowflakeTime | None = None,
        after: SnowflakeTime | None = None,
        limit: int | None = 100,
        exclude_ended: bool = False,
    ) -> EntitlementIterator:
        """Returns an :class:`.AsyncIterator` that enables fetching the user's entitlements.

        This is identical to :meth:`Client.entitlements` with the ``user`` parameter.

        .. versionadded:: 2.6

        Parameters
        ----------
        skus: list[:class:`.abc.Snowflake`] | None
            Limit the fetched entitlements to entitlements that are for these SKUs.
        before: :class:`.abc.Snowflake` | :class:`datetime.datetime` | None
            Retrieves guilds before this date or object.
            If a datetime is provided, it is recommended to use a UTC-aware datetime.
            If the datetime is naive, it is assumed to be local time.
        after: :class:`.abc.Snowflake` | :class:`datetime.datetime` | None
            Retrieve guilds after this date or object.
            If a datetime is provided, it is recommended to use a UTC-aware datetime.
            If the datetime is naive, it is assumed to be local time.
        limit: Optional[:class:`int`]
            The number of entitlements to retrieve.
            If ``None``, retrieves every entitlement, which may be slow.
            Defaults to ``100``.
        exclude_ended: :class:`bool`
            Whether to limit the fetched entitlements to those that have not ended.
            Defaults to ``False``.

        Yields
        ------
        :class:`.Entitlement`
            The application's entitlements.

        Raises
        ------
        :exc:`HTTPException`
            Retrieving the entitlements failed.
        """
        return EntitlementIterator(
            self._state,
            sku_ids=[sku.id for sku in skus] if skus else None,
            before=before,
            after=after,
            limit=limit,
            user_id=self.id,
            exclude_ended=exclude_ended,
        )
