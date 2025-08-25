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

import asyncio
from typing import TYPE_CHECKING

from .errors import VoiceGuildMismatch

if TYPE_CHECKING:
    from discord.member import VoiceState
    from discord.types.voice import VoiceState as VoiceStatePayload

    from .client import VoiceClient
    from .gateway import VoiceWebsocket


class VoiceConnectionState:
    def __init__(
        self,
        client: VoiceClient,
        ws: VoiceWebsocket,
    ) -> None:
        self.client: VoiceClient = client
        self.self_id: int = client.user.id
        self.loop: asyncio.AbstractEventLoop = client.loop

        # this is used if we don't have our self-voice state available
        self.self_mute: bool = client.self_muted
        self.self_deaf: bool = client.self_deaf

        self._updated_server: asyncio.Event = asyncio.Event()
        self._updated_state: asyncio.Event = asyncio.Event()
        self.ws: VoiceWebsocket = ws

    @property
    def connected(self) -> bool:
        return self._updated_server.is_set() and self._updated_state.is_set()

    @property
    def guild_id(self) -> int:
        return self.client.guild_id

    @property
    def voice_guild_state(self) -> VoiceState:
        return self.client.guild.me.voice

    @property
    def channel_id(self) -> int:
        return self.client.channel_id

    def update_state(self, payload: VoiceStatePayload) -> None:
        # if we're here it means the guild is found
        guild_id = int(payload["guild_id"])  # type: ignore

        if self.guild_id != guild_id:
            raise VoiceGuildMismatch(self.guild_id, guild_id)

        self.self_mute = payload["self_mute"]
        self.self_deaf = payload["self_deaf"]
