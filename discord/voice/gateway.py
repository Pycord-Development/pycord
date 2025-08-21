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
from collections.abc import Callable, Coroutine
import logging
from typing import TYPE_CHECKING, Any

import aiohttp

from discord import utils
from discord.gateway import DiscordWebSocket

from .errors import VoiceConnectionClosed

if TYPE_CHECKING:
    from .state import VoiceConnectionState

_log = logging.getLogger(__name__)


class VoiceWebsocket(DiscordWebSocket):
    if TYPE_CHECKING:
        thread_id: int
        gateway: str
        _max_heartbeat_timeout: float

    VERSION = 8

    def __init__(
        self,
        socket: aiohttp.ClientWebSocketResponse,
        loop: asyncio.AbstractEventLoop,
        state: VoiceConnectionState,
        *,
        hook: Callable[..., Coroutine[Any, Any, Any]] | None = None,
    ) -> None:
        self.ws: aiohttp.ClientWebSocketResponse = socket
        self.loop: asyncio.AbstractEventLoop = loop
        self._keep_alive: VoiceKeepAliveHandler | None = None
        self._close_code: int | None = None
        self.secrety_key: list[int] | None = None
        self.seq_ack: int = -1
        self.state: VoiceConnectionState = state

        if hook:
            self._hook = hook

    def _hook(self, *args: Any) -> Any:
        pass

    async def send_as_json(self, data: Any) -> None:
        _log.debug('Sending voice websocket frame: %s', data)
        await self.ws.send_str(utils._to_json(data))

    send_heartbeat = send_as_json

    async def resume(self) -> None:
        state = self._connection

        if not state.should_resume():
            if self.state.is_connected():
                await self.state.disconnect()
            raise VoiceConnectionClosed(
                self.ws,
                channel_id=self.state.channel_id,
                guild_id=self.state.guild_id,
                reason='The library attempted a resume when it was not expected',
            )
