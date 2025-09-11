"""
discord.voice.packets
~~~~~~~~~~~~~~~~~~~~~

Sink packet handlers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from .core import Packet
from .rtp import RTPPacket, RTCPPacket, FakePacket, ReceiverReportPacket, SenderReportPacket, SilencePacket

if TYPE_CHECKING:
    from discord import User, Member

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

    def __init__(self, packet: Packet, source: User | Member | None, *, pcm: bytes | None = None) -> None:
        self.packet: Packet = packet
        self.source: User | Member | None = source
        self.pcm: bytes = pcm if pcm else b''
