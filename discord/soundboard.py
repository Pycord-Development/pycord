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

from typing_extensions import reveal_type

from .asset import Asset
from .emoji import PartialEmoji
from .mixins import Hashable
from .types.channel import (
    VoiceChannelEffectSendEvent as VoiceChannelEffectSendEventPayload,
)
from .types.soundboard import PartialSoundboardSound as PartialSoundboardSoundPayload
from .types.soundboard import SoundboardSound as SoundboardSoundPayload
from .utils import cached_slot_property

if TYPE_CHECKING:
    from .guild import Guild
    from .http import HTTPClient
    from .member import Member
    from .state import ConnectionState


__all__ = (
    "PartialSoundboardSound",
    "SoundboardSound",
    "DefaultSoundboardSound",
)


class PartialSoundboardSound(Hashable):
    """A partial soundboard sound.

    Attributes
    ----------
    id: :class:`int`
        The sound's ID.
    volume: :class:`float`
        The sound's volume.
    emoji: :class:`PartialEmoji`
        The sound's emoji.
    """

    __slots__ = ("id", "volume", "emoji", "_http", "emoji")

    def __init__(
        self,
        data: PartialSoundboardSoundPayload | VoiceChannelEffectSendEventPayload,
        http: HTTPClient,
    ):
        self._http = http
        self._from_data(data)

    def __eq__(self, other: PartialSoundboardSound) -> bool:
        if isinstance(other, self, __class__):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other: PartialSoundboardSound) -> bool:
        return not self.__eq__(other)

    @property
    def file(self) -> Asset:
        """:class:`Asset`: Returns the sound's file."""
        return Asset._from_soundboard_sound(self, sound_id=self.id)

    def _from_data(
        self, data: PartialSoundboardSoundPayload | VoiceChannelEffectSendEventPayload
    ) -> None:
        self.id = int(data["sound_id"])
        self.volume = float(data.get("volume", 0)) or data.get("sound_volume")
        if raw_emoji := data.get(
            "emoji"
        ):  # From gateway event (VoiceChannelEffectSendEventPayload)
            self.emoji = PartialEmoji.from_dict(raw_emoji)
        elif emoji_id := data.get(
            "emoji_id", 0
        ):  # From HTTP response (PartialSoundboardSoundPayload)
            self.emoji = PartialEmoji(
                name=data.get("emoji_name"),
                id=int(emoji_id) or None,
            )


class SoundboardSound(PartialSoundboardSound):
    """Represents a soundboard sound.

    Attributes
    ----------
    id: :class:`int`
        The sound's ID.
    volume: :class:`float`
        The sound's volume.
    name: :class:`str`
        The sound's name.
    available: :class:`bool`
        Whether the sound is available.
    emoji: :class:`PartialEmoji`
        The sound's emoji.
    guild: :class:`Guild`
        The guild the sound belongs to.
    owner: :class:`Member`
        The sound's owner.
    """

    __slots__ = (
        "id",
        "volume",
        "name",
        "available",
        "emoji",
        "guild_id",
        "_cs_guild",
        "user",
        "_http",
        "_state",
        "emoji",
    )

    def __init__(
        self,
        *,
        state: ConnectionState,
        http: HTTPClient,
        data: SoundboardSoundPayload,
    ) -> None:
        self._state = state
        super().__init__(data, http)

    def _from_data(self, data: SoundboardSoundPayload) -> None:
        super()._from_data(data)
        self.name = data["name"]
        self.available: bool = data["available"]
        self.guild_id = int(data["guild_id"])
        user = data.get("user")

        self.user = self._state.store_user(user) if user else None

    @cached_slot_property("_cs_guild")
    def guild(self) -> Guild:
        """:class:`Guild`: The guild the sound belongs to.

        The :class:`Guild` object representing the guild the sound belongs to.
        .. versionadded:: 2.7
        """
        return self._state._get_guild(self.guild_id)

    def __eq__(self, other: SoundboardSound) -> bool:
        return isinstance(other, SoundboardSound) and self.__dict__ == other.__dict__

    def delete(self):
        return self._http.delete_sound(self)

    def _update(self, data: PartialSoundboardSound) -> None:
        super()._update(data)
        self.name = data["name"]
        self.available = bool(data.get("available", True))


class DefaultSoundboardSound(PartialSoundboardSound):
    """Represents a default soundboard sound.

    Attributes
    ----------
    id: :class:`int`
        The sound's ID.
    volume: :class:`float`
        The sound's volume.
    name: :class:`str`
        The sound's name.
    emoji: :class:`PartialEmoji`
        The sound's emoji.
    """

    __slots__ = ("id", "volume", "name", "emoji", "_http")

    def __init__(self, *, http: HTTPClient, data: SoundboardSoundPayload) -> None:
        super().__init__(data, http)
        self.name = data["name"]

    def __eq__(self, other: DefaultSoundboardSound) -> bool:
        return (
            isinstance(other, DefaultSoundboardSound)
            and self.__dict__ == other.__dict__
        )
