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

from typing import Literal

from .._typed_dict import NotRequired, TypedDict
from .member import MemberWithUser
from .snowflake import Snowflake

SupportedModes = Literal[
    "xsalsa20_poly1305_lite", "xsalsa20_poly1305_suffix", "xsalsa20_poly1305"
]


class _VoiceState(TypedDict):
    member: NotRequired[MemberWithUser]
    self_stream: NotRequired[bool]
    user_id: Snowflake
    session_id: str
    deaf: bool
    mute: bool
    self_deaf: bool
    self_mute: bool
    self_video: bool
    suppress: bool


class GuildVoiceState(_VoiceState):
    channel_id: Snowflake


class VoiceState(_VoiceState, total=False):
    channel_id: Snowflake | None
    guild_id: Snowflake


class VoiceRegion(TypedDict):
    id: str
    name: str
    vip: bool
    optimal: bool
    deprecated: bool
    custom: bool


class VoiceServerUpdate(TypedDict):
    token: str
    guild_id: Snowflake
    endpoint: str | None


class VoiceIdentify(TypedDict):
    server_id: Snowflake
    user_id: Snowflake
    session_id: str
    token: str


class VoiceReady(TypedDict):
    ssrc: int
    ip: str
    port: int
    modes: list[SupportedModes]
    heartbeat_interval: int
