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
import threading
from typing import TYPE_CHECKING, Any, TypeVar

from discord.opus import DecodeManager

from ._types import VoiceRecorderProtocol

if TYPE_CHECKING:
    from discord.sinks import Sink

    from .client import VoiceClient
    from .gateway import VoiceWebSocket

    VoiceClientT = TypeVar('VoiceClientT', bound=VoiceClient, covariant=True)


class VoiceRecorderClient(VoiceRecorderProtocol[VoiceClientT]):
    """Represents a voice recorder for a voice client.

    You should not construct this but instead obtain it from :attr:`VoiceClient.recorder`.

    .. versionadded:: 2.7
    """

    def __init__(self, client: VoiceClientT) -> None:
        super().__init__(client)

        self._paused: asyncio.Event = asyncio.Event()
        self._recording: asyncio.Event = asyncio.Event()
        self.decoder: DecodeManager = DecodeManager(self)
        self.sync_start: bool = False
        self.sinks: dict[int, tuple[Sink, threading.Thread]] = {}

    def is_paused(self) -> bool:
        """Whether the current recorder is paused."""
        return self._paused.is_set()

    def is_recording(self) -> bool:
        """Whether the current recording is actively recording."""
        return self._recording.is_set()

    async def hook(self, ws: VoiceWebSocket, data: dict[str, Any]) -> None:
        ...

    def record(
        self,
        sink: Sink,
    )
