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

from .appinfo import PartialApplicationInfo
from .channel import PartialChannel
from .guild import (
    GuildPreviewWithCounts,
    InviteGuild,
)
from .role import Role
from .scheduled_events import ScheduledEvent
from .user import PartialUser, User

InviteTargetType = Literal[
    1,  # STREAM
    2,  # EMBEDDED_APPLICATION
]


class VanityInvite(TypedDict):
    code: str | None
    uses: int


class IncompleteInvite(TypedDict):
    code: str
    channel: PartialChannel
    uses: NotRequired[int]
    max_uses: NotRequired[int]
    max_age: NotRequired[int]
    temporary: NotRequired[bool]
    expires_at: str | None


InviteType = Literal[
    0,  # GUILD
    1,  # GROUP_DM
    2,  # FRIEND
]


class Invite(IncompleteInvite):
    type: InviteType
    guild: NotRequired[InviteGuild]
    inviter: NotRequired[User]
    scheduled_event: NotRequired[ScheduledEvent]
    target_user: NotRequired[PartialUser]
    target_type: NotRequired[InviteTargetType]
    target_application: NotRequired[PartialApplicationInfo]
    flags: NotRequired[int]
    roles: NotRequired[list[Role]]  # Partial role


class InviteWithCounts(Invite, GuildPreviewWithCounts):
    pass


TargetUsersJobStatus = Literal[
    0,  # UNSPECIFIED
    1,  # PROCESSING
    2,  # COMPLETED
    3,  # FAILED
]


class InviteTargetUsersJobStatus(TypedDict):
    """The object returned when getting the process of processing invite target users"""

    status: TargetUsersJobStatus
    total_users: int
    processed_users: int
    created_at: NotRequired[str]
    completed_at: NotRequired[str | None]
    error_message: NotRequired[str]
