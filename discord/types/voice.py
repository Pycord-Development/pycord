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

from typing import TYPE_CHECKING, Literal, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .member import Member
    from .snowflake import Snowflake

SupportedModes = Literal[
    "xsalsa20_poly1305_lite",
    "xsalsa20_poly1305_suffix",
    "xsalsa20_poly1305",
    "aead_xchacha20_poly1305_rtpsize",
]


class VoiceState(TypedDict):
    guild_id: NotRequired[Snowflake]
    channel_id: Snowflake | None
    user_id: Snowflake
    member: NotRequired[Member]
    session_id: str
    deaf: bool
    mute: bool
    self_deaf: bool
    self_mute: bool
    self_stream: NotRequired[bool]
    self_video: bool
    suppress: bool
    request_to_speak_timestamp: str | None


GuildVoiceState = VoiceState


class VoiceRegion(TypedDict):
    id: str
    name: str
    optimal: bool
    deprecated: bool
    custom: bool


class VoiceIdentify(TypedDict):
    """Fields to send when establishing a voice websocket connection"""

    server_id: Snowflake
    user_id: Snowflake
    session_id: str
    token: str
    max_dave_protocol_version: int


class VoiceReady(TypedDict):
    """Fields received when the voice websocket connection is ready"""

    ssrc: int
    ip: str
    port: int
    modes: list[SupportedModes]


class VoiceHello(TypedDict):
    heartbeat_interval: int
    v: int  # Voice gateway version


class VoiceHeartbeat(TypedDict):
    """Heartbeat payload to send at the interval specified in :class:`VoiceHello`, starting from voice version 8"""

    t: int
    seq_ack: int


class VoiceHeartbeatAck(TypedDict):
    """Heartbeat ACK payload received, starting from voice version 8"""

    t: int
