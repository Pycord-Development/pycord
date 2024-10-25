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

from typing_extensions import override, reveal_type

from .asset import Asset
from .emoji import PartialEmoji
from .mixins import Hashable
from .types.channel import (
    VoiceChannelEffectSendEvent as VoiceChannelEffectSendEventPayload,
)
from .types.soundboard import SoundboardSound as SoundboardSoundPayload
from .utils import cached_slot_property

if TYPE_CHECKING:
    from .guild import Guild
    from .http import HTTPClient
    from .state import ConnectionState


__all__ = (
    "PartialSoundboardSound",
    "SoundboardSound",
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

    __slots__ = ("id", "volume", "emoji", "_http", "_state")

    def __init__(
        self,
        data: SoundboardSoundPayload | VoiceChannelEffectSendEventPayload,
        state: ConnectionState,
        http: HTTPClient,
    ):
        self._http = http
        self._state = state
        self._from_data(data)

    def _from_data(
        self, data: SoundboardSoundPayload | VoiceChannelEffectSendEventPayload
    ) -> None:
        self.id = int(data.get("sound_id", 0))
        self.volume = (
            float(data.get("volume", 0) or data.get("sound_volume", 0)) or None
        )
        if raw_emoji := data.get(
            "emoji"
        ):  # From gateway event (VoiceChannelEffectSendEventPayload)
            self.emoji = PartialEmoji.from_dict(raw_emoji)
        else:  # From HTTP response (SoundboardSoundPayload)
            self.emoji = PartialEmoji(
                name=data.get("emoji_name"),
                id=int(data.get("emoji_id", 0) or 0) or None,
            )

    @override
    def __eq__(
        self, other: PartialSoundboardSound
    ) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(other, self, __class__):
            return self.id == other.id
        return NotImplemented

    @override
    def __ne__(
        self, other: PartialSoundboardSound
    ) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        return not self.__eq__(other)

    @property
    def file(self) -> Asset:
        """:class:`Asset`: Returns the sound's file."""
        return Asset._from_soundboard_sound(self._state, sound_id=self.id)

    def __repr__(self) -> str:
        return f"<PartialSoundboardSound id={self.id} volume={self.volume} emoji={self.emoji!r}>"


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
        "name",
        "available",
        "guild_id",
        "user",
        "_cs_guild",
        "_state",
    )

    def __init__(
        self,
        *,
        state: ConnectionState,
        http: HTTPClient,
        data: SoundboardSoundPayload,
    ) -> None:
        super().__init__(data, state, http)

    @override
    def _from_data(
        self, data: SoundboardSoundPayload
    ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        super()._from_data(data)
        self.name = data["name"]
        self.available: bool = data["available"]
        self.guild_id = int(data.get("guild_id", 0) or 0) or None
        user = data.get("user")
        self.user = self._state.store_user(user) if user else None

    @cached_slot_property("_cs_guild")
    def guild(self) -> Guild | None:
        """:class:`Guild`: The guild the sound belongs to.

        The :class:`Guild` object representing the guild the sound belongs to.
        .. versionadded:: 2.7
        """
        return self._state._get_guild(self.guild_id) if self.guild_id else None

    @override
    def __eq__(
        self, other: SoundboardSound
    ) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        return isinstance(other, SoundboardSound) and self.__dict__ == other.__dict__

    @property
    def is_default_sound(self) -> bool:
        """:class:`bool`: Whether the sound is a default sound."""
        return self.guild_id is None

    def delete(self, *, reason: str | None = None) -> Coroutine[Any, Any, None]:
        if self.is_default_sound:
            raise ValueError("Cannot delete a default sound.")
        return self._http.delete_sound(self, reason=reason)

    @override
    def __repr__(self) -> str:
        return f"<SoundboardSound id={self.id} name={self.name!r} volume={self.volume} emoji={self.emoji!r} guild={self.guild!r} user={self.user!r} available={self.available} default={self.is_default_sound}>"
