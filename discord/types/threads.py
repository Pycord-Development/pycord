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

from typing_extensions import NotRequired, TypedDict

from ..flags import ChannelFlags
from .snowflake import Snowflake

ThreadType = Literal[10, 11, 12]
ThreadArchiveDuration = Literal[60, 1440, 4320, 10080]


class ThreadMember(TypedDict):
    id: Snowflake
    user_id: Snowflake
    join_timestamp: str
    flags: int


class ThreadMetadata(TypedDict):
    invitable: NotRequired[bool]
    create_timestamp: NotRequired[str]
    archived: bool
    auto_archive_duration: ThreadArchiveDuration
    archive_timestamp: str
    locked: bool


class Thread(TypedDict):
    member: NotRequired[ThreadMember]
    last_message_id: NotRequired[Snowflake | None]
    last_pin_timestamp: NotRequired[Snowflake | None]
    id: Snowflake
    guild_id: Snowflake
    parent_id: Snowflake
    owner_id: Snowflake
    name: str
    type: ThreadType
    member_count: int
    message_count: int
    rate_limit_per_user: int
    thread_metadata: ThreadMetadata
    flags: ChannelFlags
    total_message_sent: int


class ThreadPaginationPayload(TypedDict):
    threads: list[Thread]
    members: list[ThreadMember]
    has_more: bool
