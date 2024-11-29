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

from typing import TYPE_CHECKING, Any, Coroutine

from . import utils
from .abc import Snowflake
from .colour import Color, Colour
from .emoji import Emoji, PartialEmoji
from .enums import ChannelType, VoiceRegion
from .flags import SystemChannelFlags
from .guild import Guild
from .permissions import PermissionOverwrite, Permissions
from .state import ConnectionState

if TYPE_CHECKING:
    from .types.guild import GuildCreate as GuildCreatePayload
    from .types.role import Role as RolePayload

MISSING = utils.MISSING

__all__ = (
    "GuildBuilder",
    "GuildBuilderChannel",
    "GuildBuilderRole",
)


class GuildBuilder:
    """Represents a Discord guild that is yet to be created.

    This is returned by :meth:`Client.create_guild` to allow users to modify the guild
    properties before creating it.

    .. versionadded:: 2.7

    Attributes
    ----------
    code: Optional[:class:`str`]
        The guild template code that the guild is going to be created with.
    afk_channel_id: Optional[:class:`int`]
        The AFK channel ID. Defaults to ``None``.
    system_channel_id: Optional[:class:`int`]
        The system channel ID. Defaults to ``None``.
    system_channel_flags: Optional[:class:`SystemChannelFlags`]
        The system channel flags. Defaults to ``None``. This requires :attr:`.system_channel_id` to be
        not ``None``.
    """

    __slots__ = (
        "_state",
        "_name",
        "_icon",
        "_channels",
        "_roles",
        "_metadata",
        "afk_channel_id",
        "system_channel_id",
        "system_channel_flags",
        "code",
    )

    def __init__(
        self,
        *,
        state: ConnectionState,
        name: str,
        icon: bytes,
        code: str | None,
        metadata: dict[str, Any],
    ) -> None:
        self._state: ConnectionState = state
        self._name: str = name
        self._icon: bytes = icon
        self._channels: dict[int, GuildBuilderChannel] = {}
        self._roles: dict[int, GuildBuilderRole] = {}
        self._metadata: dict[str, Any] = metadata
        self.code: str | None = code
        self.afk_channel_id: int | None = None
        self.system_channel_id: int | None = None
        self.system_channel_flags: SystemChannelFlags | None = None

    async def _do_create(self) -> Guild:
        http = self._state.http
        if self.code is not None:
            data = await http.create_from_template(
                self.code,
                self.name,
                utils._bytes_to_base64_data(self.icon) if self.icon else None,
            )
            return Guild(data=data, state=self._state)

        payload: GuildCreatePayload = {
            "name": self.name,
        }
        payload.update(self._metadata)  # type: ignore

        if self._icon is not MISSING:
            payload["icon"] = utils._bytes_to_base64_data(self._icon)
        if self._channels is not MISSING:
            payload["channels"] = [ch.to_dict() for ch in self._channels.values()]
        if self._roles is not MISSING:
            payload["roles"] = [role.to_dict() for role in self._roles.values()]
        if self.afk_channel_id is not None:
            payload["afk_channel_id"] = self.afk_channel_id
        if self.system_channel_id is not None:
            payload["system_channel_id"] = self.system_channel_id
        if self.system_channel_flags is not None:
            payload["system_channel_flags"] = self.system_channel_flags.value

        data = await http.create_guild(payload)
        return Guild(data=data, state=self._state)

    async def __await__(self) -> Guild:
        return await self._do_create()

    def __call__(self) -> Coroutine[Any, Any, Guild]:
        return self._do_create()

    @property
    def channels(self) -> list[GuildBuilderChannel]:
        """List[:class:`GuildBuilderChannel`]: Returns a read-only list containing all the
        channels that are going to be created along the guild.
        """
        if self._channels is MISSING:
            return []
        return list(self._channels.values())

    @property
    def roles(self) -> list[GuildBuilderRole]:
        """List[:class:`GuildBuilderRole`]: Returns a read-only list containing all the roles
        that are going to be created along the guild.
        """
        if self._roles is MISSING:
            return []
        return list(self._roles.values())

    @property
    def name(self) -> str:
        """:class:`str`: Returns the name of the guild that is going to be created."""
        return self._name

    @property
    def icon(self) -> bytes | None:
        """Optional[:class:`bytes`]: Returns the icon of the guild that is going to be created."""
        return self._icon if self._icon is not MISSING else None

    def add_channel(
        self,
        name: str,
        type: ChannelType,
        *,
        topic: str | None = None,
        overwrites: dict[Snowflake, PermissionOverwrite] = MISSING,
        nsfw: bool = MISSING,
        category_id: int | None = None,
    ) -> GuildBuilderChannel:
        """Adds a channel to the current guild.

        Parameters
        ----------
        name: :class:`str`
            The channel name.
        type: :class:`ChannelType`
            The channel type.
        topic: Optional[:class:`str`]
            The channel topic.
        overwrites: Dict[:class:`~discord.abc.Snowflake`, :class:`PermissionOverwrite`]
            The channel overwrites.
        nsfw: :class:`bool`
            Whether the channel is NSFW flagged.
        category_id: Optional[:class:`int`]
            The category placeholder ID this channel belongs to.

        Returns
        -------
        :class:`GuildBuilderChannel`
            The channel.
        """

        id = len(self._channels) + 1
        metadata = {}

        if overwrites is not MISSING:
            metadata["overwrites"] = overwrites

        channel = self._channels[id] = GuildBuilderChannel(
            id=id,
            name=name,
            type=type,
            topic=topic,
            nsfw=nsfw,
            category_id=category_id,
            metadata=metadata,
        )
        return channel

    def _create_default_role(self) -> GuildBuilderRole:
        return GuildBuilderRole(
            id=0,
            name="everyone",
            hoisted=True,
            position=0,
            mentionable=True,
            permissions=Permissions.text(),
            colour=Colour(0),
            icon=None,
        )

    def edit_default_role_permissions(
        self,
        perms_obj: Permissions | None = None,
        **perms: bool,
    ) -> GuildBuilderRole:
        """Edits the default role permissions and returns it.

        Parameters
        ----------
        perms_obj: Optional[:class:`Permissions`]
            The permissions object. This is merged with ``perms``, if provided.
        **perms: :class:`bool`
            The permissions to allow or deny. This is merged with ``perms_obj``, if provided.

        Returns
        -------
        :class:`GuildBuilderRole`
            The default role.
        """

        default_role = self._roles.get(0)

        if default_role is None:
            default_role = self._roles[0] = self._create_default_role()

        resolved = Permissions(**perms)
        if perms_obj is not None:
            resolved |= perms_obj

        default_role.permissions = resolved
        return default_role

    def add_role(
        self,
        name: str,
        *,
        permissions: Permissions = MISSING,
        hoisted: bool = False,
        position: int = MISSING,
        mentionable: bool = True,
        colour: Colour | None = MISSING,
        color: Color | None = MISSING,
        icon: bytes | None = None,
        emoji: str | PartialEmoji | Emoji | None = None,
    ) -> GuildBuilderRole:
        """Adds a role to the current guild.

        Parameters
        ----------
        name: :class:`str`
            The role name.
        permissions: :class:`Permissions`
            The role permissions.
        hoisted: :class:`bool`
            Whether the role members are displayed separately in the sidebar.
            Defaults to ``False``.
        position: :class:`int`
            The role position.
        mentionable: :class:`bool`
            Whether everyone can mention this role. Defaults to ``True``.
        colour: :class:`Colour`
            The role colour.
        color: :class:`Color`
            The role color. This is an alias for ``colour``.
        icon: Optional[:class:`bytes`]
            The role icon.
        emoji: Optional[Union[:class:`str`, :class:`PartialEmoji`, :class:`Emoji`]]
            The role displayed emoji.

        Returns
        -------
        :class:`GuildBuilderRole`
            The role.
        """

        if not len(self._roles) > 1:
            # If we add this role to the 0 index then we are editing
            # the default role.
            self._roles[0] = self._create_default_role()

        id = len(self._roles) + 1

        if colour is not MISSING and color is not MISSING:
            raise TypeError("Cannot provide both colour and color")

        resolved_colour = colour if colour is not MISSING else color

        if resolved_colour in (MISSING, None):
            resolved_colour = Colour(0)

        if permissions is MISSING:
            permissions = self._roles[0].permissions
        if position is MISSING:
            position = id

        role = self._roles[id] = GuildBuilderRole(
            id=id,
            name=name,
            hoisted=hoisted,
            position=position,
            mentionable=mentionable,
            permissions=permissions,
            colour=resolved_colour,
            icon=icon,
        )
        role.emoji = emoji
        return role


class GuildBuilderChannel:
    """Represents a :class:`GuildBuilder` channel.

    .. versionadded:: 2.7

    Attributes
    ----------
    id: :class:`int`
        The placeholder channel ID.
    name: :class:`str`
        The channel name.
    type: :class:`ChannelType`
        The channel type.
    topic: Optional[:class:`str`]
        The channel topic.
    nsfw: :class:`bool`
        Whether the channel is NSFW flagged.
    category_id: Optional[:class:`int`]
        The category placeholder ID this channel belongs to.
    """

    __slots__ = (
        "id",
        "name",
        "type",
        "topic",
        "nsfw",
        "category_id",
        "_metadata",
    )

    def __init__(
        self,
        id: int,
        name: str,
        type: ChannelType,
        topic: str | None,
        nsfw: bool,
        category_id: int | None,
        metadata: dict[str, Any],
    ) -> None:
        self.id: int = id
        self.name: str = name
        self.type: ChannelType = type
        self.topic: str | None = topic
        self.nsfw: bool = nsfw
        self.category_id: int | None = category_id
        self._metadata: dict[str, Any] = metadata

    @property
    def overwrites(self) -> dict[Snowflake, PermissionOverwrite]:
        """Dict[:class:`Object`, :class:`PermissionOverwrite`]: Returns this channel's role overwrites."""
        return self._metadata.get("overwrites", {})

    @overwrites.setter
    def overwrites(self, ow: dict[Snowflake, PermissionOverwrite] | None) -> None:
        if ow is not None:
            self._metadata["ovewrites"] = ow
        else:
            self._metadata.pop("overwrites", None)

    @property
    def bitrate(self) -> int | None:
        """Optional[:class:`int`]: Returns the channel bitrate.

        This will return ``None`` if :attr:`GuildBuilderChannel.type` is not
        :attr:`ChannelType.voice` or :attr:`ChannelType.stage_voice`.
        """
        return self._metadata.get("bitrate")

    @bitrate.setter
    def bitrate(self, value: int | None) -> None:
        if self.type not in (ChannelType.voice, ChannelType.stage_voice):
            raise ValueError("cannot set a bitrate to a non-voice channel")

        if value is not None:
            self._metadata["bitrate"] = value
        else:
            self._metadata.pop("bitrate", None)

    @property
    def user_limit(self) -> int | None:
        """Optional[:class:`int`]: Returns the channel limit for number of members that
        can be connected in the channel.

        This will return ``None`` if :attr:`GuildBuilderChannel.type` is not
        :attr:`ChannelType.voice` or :attr:`ChannelType.stage_voice`.
        """
        return self._metadata.get("user_limit")

    @user_limit.setter
    def user_limit(self, value: int | None) -> None:
        if self.type not in (ChannelType.voice, ChannelType.stage_voice):
            raise ValueError("cannot set a user_limit to a non-voice channel")

        if value is not None:
            self._metadata["user_limit"] = value
        else:
            self._metadata.pop("bitrate", None)

    @property
    def slowmode_delay(self) -> int:
        """:class:`int`: The number of seconds a member must wait between sending messages
        in this channel. A value of ``0`` denotes that it is disabled.
        """
        return self._metadata.get("rate_limit_per_user", 0)

    @slowmode_delay.setter
    def slowmode_delay(self, value: int | None) -> None:
        if value is not None and value != 0:
            self._metadata["rate_limit_per_user"] = value
        else:
            self._metadata.pop("rate_limit_per_user", None)

    @property
    def rtc_region(self) -> VoiceRegion | None:
        """Optional[:class:`VoiceRegion`]: Returns the channel voice region.

        This will return ``None`` if :attr:`GuildBuilderChannel.type` is not
        :attr:`ChannelType.voice` or :attr:`ChannelType.stage_voice`.
        """
        return self._metadata.get("rtc_region")

    @rtc_region.setter
    def rtc_region(self, region: VoiceRegion | None) -> None:
        if self.type not in (ChannelType.voice, ChannelType.stage_voice):
            raise ValueError("cannot set rtc_region to a non-voice channel")

        if region is not None:
            self._metadata["rtc_region"] = region
        else:
            self._metadata.pop("rtc_region", None)

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "id": str(self.id),
            "name": self.name,
            "type": self.type.value,
            "nsfw": self.nsfw,
            "topic": self.topic,
        }

        overwrites: dict[Snowflake, PermissionOverwrite] | None = self._metadata.get(
            "overwrites", None
        )
        if overwrites is not None:
            pairs = []

            for target, ow in overwrites.items():
                allowed, denied = ow.pair()
                pairs.append(
                    {
                        "target": target.id,
                        "type": 0,  # role,
                        "allow": allowed.value,
                        "deny": denied.value,
                    },
                )

            payload["permission_overwrites"] = pairs

        if bitrate := self._metadata.get("bitrate"):
            payload["bitrate"] = bitrate

        if user_limit := self._metadata.get("user_limit"):
            payload["user_limit"] = user_limit

        if slowmode := self._metadata.get("rate_limit_per_user"):
            payload["rate_limit_per_user"] = slowmode

        if rtc_region := self._metadata.get("rtc_region"):
            payload["rtc_region"] = rtc_region.value

        # TODO: add more fields

        return payload


class GuildBuilderRole:
    """Represents a :class:`GuildBuilder` role.

    .. versionadded:: 2.7

    Attributes
    ----------
    id: :class:`int`
        The placeholder role ID.
    name: :class:`str`
        The role name.
    hoisted: :class:`bool`
        Whether the role is hoisted.
    position: :class:`int`
        The role position.
    mentionable: :class:`bool`
        Whether the role is mentionable.
    permissions: :class:`Permissions`
        The permissions of this role.
    icon: Optional[:class:`bytes`]
        The emoji icon.
    """

    __slots__ = (
        "id",
        "name",
        "hoisted",
        "position",
        "mentionable",
        "permissions",
        "_colour",
        "icon",
        "_unicode_emoji",
    )

    def __init__(
        self,
        id: int,
        name: str,
        hoisted: bool,
        position: int,
        mentionable: bool,
        permissions: Permissions,
        colour: Colour,
        icon: bytes | None,
    ) -> None:
        self.id: int = id
        self.name: str = name
        self.hoisted: bool = hoisted
        self.position: int = position
        self.mentionable: bool = mentionable
        self.permissions: Permissions = permissions
        self._colour: int = colour.value
        self.icon: bytes | None = icon
        self._unicode_emoji: str | None = None

    @property
    def colour(self) -> Colour:
        """:class:`Colour`: Returns this role colour. There is an alias for this named :attr:`.color`."""
        return Colour(self._colour)

    @colour.setter
    def colour(self, value: Colour | None) -> None:
        if value is not None:
            self._colour = value.value
        else:
            self._colour = 0

    @property
    def color(self) -> Color:
        """:class:`Color`: Returns this role color. There is an alias for this named :attr:`.colour`."""
        return self.colour

    @color.setter
    def color(self, value: Color | None) -> None:
        self.colour = value

    @property
    def emoji(self) -> PartialEmoji | None:
        """Optional[:class:`PartialEmoji`]: Returns the displayed emoji of this role."""
        if self._unicode_emoji is None:
            return None
        return PartialEmoji.from_str(self._unicode_emoji)

    @emoji.setter
    def emoji(self, value: str | PartialEmoji | Emoji | None) -> None:
        if value is None:
            self._unicode_emoji = None
            return

        if isinstance(value, str):
            self._unicode_emoji = value
        elif isinstance(value, (PartialEmoji, Emoji)):
            self._unicode_emoji = str(value)
        else:
            raise TypeError(
                f"expected a str, PartialEmoji, Emoji or None, not {value.__class__.__name__}"
            )

    def to_dict(self) -> RolePayload:
        payload: RolePayload = {
            "id": str(self.id),
            "name": self.name,
            "hoist": self.hoisted,
            "color": self._colour,
            "mentionable": self.mentionable,
            "permissions": str(self.permissions.value),
            "position": self.position,
            "icon": (
                utils._bytes_to_base64_data(self.icon)
                if self.icon is not None
                else None
            ),
            "unicode_emoji": self._unicode_emoji,
        }  # type: ignore
        return payload
