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

from aiohttp import ClientWebSocketResponse

from discord.errors import ClientException


class VoiceConnectionClosed(ClientException):
    """Exception that's raised when a voice websocket connection
    is closed for reasons that could not be handled internally.

    Attributes
    ----------
    code: :class:`int`
        The close code of the websocket.
    reason: :class:`str`
        The reason provided for the closure.
    guild_id: :class:`int`
        The guild ID the client was connected to.
    channel_id: :class:`int`
        The channel ID the client was connected to.
    """

    __slots__ = (
        "code",
        "reason",
        "channel_id",
        "guild_id",
    )

    def __init__(
        self,
        socket: ClientWebSocketResponse,
        channel_id: int,
        guild_id: int,
        *,
        reason: str | None = None,
        code: int | None = None,
    ) -> None:
        self.code: int = code or socket.close_code or -1
        self.reason: str = reason if reason is not None else ""
        self.channel_id: int = channel_id
        self.guild_id: int = guild_id
        super().__init__(
            f"The voice connection on {self.channel_id} (guild {self.guild_id}) was closed with {self.code}",
        )


class VoiceGuildMismatch(ClientException):
    """Exception that's raised when, while connecting to a voice channel, the data
    the library has differs from the one discord sends.

    Attributes
    ----------
    expected: :class:`int`
        The expected guild ID. This is the one the library has.
    received: :class:`int`
        The received guild ID. This is the one sent by discord.
    """

    __slots__ = (
        "expected",
        "received",
    )

    def __init__(self, expt: int, recv: int) -> None:
        self.expected: int = expt
        self.received: int = recv
