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

from typing import TypedDict

from typing_extensions import NotRequired

from .collectibles import AvatarDecoration, Collectibles
from .snowflake import Snowflake, SnowflakeList
from .user import User


class PartialMember(TypedDict):
    """A guild member without ``user``.

    Sent as ``member`` and ``mentions[].member`` in MESSAGE_CREATE / MESSAGE_UPDATE,
    and in interaction ``resolved.members`` (which also omits ``deaf`` and ``mute``).
    """

    nick: NotRequired[str | None]
    avatar: NotRequired[str | None]
    banner: NotRequired[str | None]
    roles: SnowflakeList
    joined_at: str | None
    premium_since: NotRequired[str | None]
    deaf: NotRequired[bool]  # Required for a fully resolved member
    mute: NotRequired[bool]  # Required for a fully resolved member
    flags: int
    pending: NotRequired[bool]
    permissions: NotRequired[str]
    communication_disabled_until: NotRequired[str | None]
    avatar_decoration_data: NotRequired[AvatarDecoration | None]
    collectibles: NotRequired[Collectibles | None]


class Member(PartialMember):
    user: User


class UserWithMember(User):
    """A user with a partial ``member`` attached, such as in message ``mentions``."""

    member: NotRequired[PartialMember]


class MemberUpdateEvent(TypedDict):
    guild_id: Snowflake
    roles: list[Snowflake]
    user: User
    nick: NotRequired[str | None]
    avatar: str | None
    banner: str | None
    joined_at: str | None
    premium_since: NotRequired[str | None]
    deaf: NotRequired[bool]
    mute: NotRequired[bool]
    pending: NotRequired[bool]
    communication_disabled_until: NotRequired[str | None]
    avatar_decoration_data: NotRequired[AvatarDecoration | None]
    collectibles: NotRequired[Collectibles | None]
