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

from typing import Literal, Union

from .._typed_dict import NotRequired, TypedDict
from ..enums import SortOrder
from ..flags import ChannelFlags
from .snowflake import Snowflake
from .threads import ThreadArchiveDuration, ThreadMember, ThreadMetadata
from .user import PartialUser

OverwriteType = Literal[0, 1]


class PermissionOverwrite(TypedDict):
    id: Snowflake
    type: OverwriteType
    allow: str
    deny: str


ChannelType = Literal[0, 1, 2, 3, 4, 5, 10, 11, 12, 13]


class _BaseChannel(TypedDict):
    id: Snowflake
    name: str


class _BaseGuildChannel(_BaseChannel):
    guild_id: Snowflake
    position: int
    permission_overwrites: list[PermissionOverwrite]
    nsfw: bool
    parent_id: Snowflake | None


class PartialChannel(_BaseChannel):
    type: ChannelType


class _TextChannelOptional(TypedDict, total=False):
    topic: str
    last_message_id: Snowflake | None
    last_pin_timestamp: str
    rate_limit_per_user: int
    default_auto_archive_duration: ThreadArchiveDuration
    default_thread_rate_limit_per_user: int


class TextChannel(_BaseGuildChannel, _TextChannelOptional):
    type: Literal[0]


class DefaultReaction(TypedDict):
    emoji_id: NotRequired[Snowflake | None]
    emoji_name: NotRequired[str | None]


class ForumTag(TypedDict):
    id: Snowflake
    name: str
    moderated: bool
    emoji_id: NotRequired[Snowflake | None]
    emoji_name: NotRequired[str | None]


class ForumChannel(_BaseGuildChannel, _TextChannelOptional):
    type: Literal[15]
    available_tags: NotRequired[list[ForumTag] | None]
    default_reaction_emoji: NotRequired[DefaultReaction | None]
    default_sort_order: NotRequired[SortOrder | None]
    flags: ChannelFlags


class NewsChannel(_BaseGuildChannel, _TextChannelOptional):
    type: Literal[5]


VideoQualityMode = Literal[1, 2]


class VoiceChannel(_BaseGuildChannel):
    rtc_region: NotRequired[str | None]
    video_quality_mode: NotRequired[VideoQualityMode]
    type: Literal[2]
    bitrate: int
    user_limit: int


class CategoryChannel(_BaseGuildChannel):
    type: Literal[4]


class StageChannel(_BaseGuildChannel):
    rtc_region: NotRequired[str | None]
    topic: NotRequired[str]
    type: Literal[13]
    bitrate: int
    user_limit: int


class ThreadChannel(_BaseChannel):
    member: NotRequired[ThreadMember]
    owner_id: NotRequired[Snowflake]
    rate_limit_per_user: NotRequired[int]
    last_message_id: NotRequired[Snowflake | None]
    last_pin_timestamp: NotRequired[str]
    type: Literal[10, 11, 12]
    guild_id: Snowflake
    parent_id: Snowflake
    nsfw: bool
    message_count: int
    member_count: int
    thread_metadata: ThreadMetadata
    applied_tags: NotRequired[list[Snowflake] | None]
    flags: ChannelFlags
    total_message_sent: int


GuildChannel = Union[
    TextChannel,
    NewsChannel,
    VoiceChannel,
    CategoryChannel,
    StageChannel,
    ThreadChannel,
    ForumChannel,
]


class DMChannel(TypedDict):
    id: Snowflake
    type: Literal[1]
    last_message_id: Snowflake | None
    recipients: list[PartialUser]


class GroupDMChannel(_BaseChannel):
    type: Literal[3]
    icon: str | None
    owner_id: Snowflake


Channel = Union[GuildChannel, DMChannel, GroupDMChannel]

PrivacyLevel = Literal[1, 2]


class StageInstance(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    channel_id: Snowflake
    topic: str
    privacy_level: PrivacyLevel
    discoverable_disabled: bool
    guild_scheduled_event_id: Snowflake
