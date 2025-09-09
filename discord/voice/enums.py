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

from discord.enums import Enum


class OpCodes(Enum):
    identify = 0
    select_protocol = 1
    ready = 2
    heartbeat = 3
    session_description = 4
    speaking = 5
    heartbeat_ack = 6
    resume = 7
    hello = 8
    resumed = 9
    client_connect = 10
    client_disconnect = 11

    # dave protocol stuff
    dave_prepare_transition = 21
    dave_execute_transition = 22
    dave_transition_ready = 23
    dave_prepare_epoch = 24
    mls_external_sender_package = 25
    mls_key_package = 26
    mls_proposals = 27
    mls_commit_welcome = 28
    mls_commit_transition = 29
    mls_welcome = 30
    mls_invalid_commit_welcome = 31

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int):
            return self.value == other
        elif isinstance(other, self.__class__):
            return self is other
        return NotImplemented

    def __int__(self) -> int:
        return self.value


class ConnectionFlowState(Enum):
    disconnected = 0
    set_guild_voice_state = 1
    got_voice_state_update = 2
    got_voice_server_update = 3
    got_both_voice_updates = 4
    websocket_connected = 5
    got_websocket_ready = 6
    got_ip_discovery = 7
    connected = 8
