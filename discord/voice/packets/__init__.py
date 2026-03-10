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

from .core import Packet
from .rtp import (
    FakePacket,
    ReceiverReportPacket,
    RTCPPacket,
    RTPPacket,
    SenderReportPacket,
    SilencePacket,
)

if TYPE_CHECKING:
    from discord import Member, User

__all__ = (
    "Packet",
    "RTPPacket",
    "RTCPPacket",
    "FakePacket",
    "ReceiverReportPacket",
    "SenderReportPacket",
    "SilencePacket",
    "VoiceData",
)


class VoiceData:
    """Represents an audio data from a source.

    .. versionadded:: 2.7

    Attributes
    ----------
    packet: :class:`~discord.sinks.Packet`
        The packet this source data contains.
    source: :class:`~discord.User` | :class:`~discord.Member` | None
        The user that emitted this audio source.
    pcm: :class:`bytes`
        The PCM bytes of this source.
    """

    def __init__(
        self, packet: Packet, source: User | Member | None, *, pcm: bytes | None = None
    ) -> None:
        self.packet: Packet = packet
        self.source: User | Member | None = source
        self.pcm: bytes = pcm if pcm else b""

    @property
    def opus(self) -> bytes | None:
        return self.packet.decrypted_data
