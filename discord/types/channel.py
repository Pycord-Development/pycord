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
    from .snowflake import Snowflake
    from .thread import ThreadArchiveDuration, ThreadMember, ThreadMetadata, ThreadType
    from .user import User

OverwriteType = Literal[
    0,  # Role
    1,  # Member
]


class PermissionOverwrite(TypedDict):
    id: Snowflake
    type: OverwriteType
    allow: str
    deny: str


ChannelType = Literal[
    0,  # GUILD_TEXT
    1,  # DM
    2,  # GUILD_VOICE
    3,  # GROUP_DM
    4,  # GUILD_CATEGORY
    5,  # GUILD_ANNOUNCEMENT
    10,  # ANNOUNCEMENT_THREAD
    11,  # PUBLIC_THREAD
    12,  # PRIVATE_THREAD
    13,  # GUILD_STAGE_VOICE
    14,  # GUILD_DIRECTORY
    15,  # GUILD_FORUM
    16,  # GUILD_MEDIA
]


class _BaseChannel(TypedDict):
    id: Snowflake
    flags: NotRequired[int]


class _BaseGuildChannel(_BaseChannel):
    guild_id: NotRequired[Snowflake]
    position: int
    permission_overwrites: list[PermissionOverwrite]
    name: str
    nsfw: bool
    parent_id: Snowflake | None  # Always None for categories


class PartialChannel(_BaseChannel):
    """For partially resolved channels in invites and interactions"""

    type: ChannelType
    name: NotRequired[str | None]


class _MessageableChannel(TypedDict):
    """Every channel that can be used to send messages"""

    last_message_id: NotRequired[Snowflake | None]
    last_pin_timestamp: NotRequired[str | None]
    rate_limit_per_user: NotRequired[int]


class _ThreadParentChannel(TypedDict):
    """Every channel that can have threads"""

    topic: NotRequired[str | None]
    default_auto_archive_duration: NotRequired[ThreadArchiveDuration]
    default_thread_rate_limit_per_user: NotRequired[int]


class TextChannel(_BaseGuildChannel, _MessageableChannel, _ThreadParentChannel):
    type: Literal[0]


class NewsChannel(_BaseGuildChannel, _MessageableChannel, _ThreadParentChannel):
    type: Literal[5]


class Thread(_BaseChannel, _MessageableChannel):
    """The type for an actual thread itself"""

    member: NotRequired[ThreadMember]
    owner_id: NotRequired[Snowflake]
    type: ThreadType
    guild_id: Snowflake
    name: str
    parent_id: Snowflake
    nsfw: bool
    message_count: int
    member_count: int  # Maximum of 50 counted
    thread_metadata: ThreadMetadata
    applied_tags: NotRequired[list[Snowflake]]
    total_message_sent: int


class DefaultReaction(TypedDict):
    emoji_id: Snowflake | None
    emoji_name: str | None


class ForumTag(TypedDict):
    id: Snowflake
    name: str
    moderated: bool
    emoji_id: Snowflake | None
    emoji_name: str | None


SortOrder = Literal[
    0,  # LATEST_ACTIVITY
    1,  # CREATION_DATE
]

ForumLayout = Literal[
    0,  # NOT_SET
    1,  # LIST_VIEW
    2,  # GALLERY_VIEW
]


class _BaseThreadedChannel(_BaseGuildChannel, _ThreadParentChannel):
    """Type for thread-only channels like :class:`ForumChannel` and :class:`MediaChannel`"""

    last_message_id: NotRequired[Snowflake | None]
    rate_limit_per_user: NotRequired[int]
    available_tags: NotRequired[list[ForumTag]]
    default_reaction_emoji: NotRequired[DefaultReaction | None]
    default_sort_order: NotRequired[SortOrder | None]
    flags: int


class MediaChannel(_BaseThreadedChannel):
    type: Literal[16]


class ForumChannel(_BaseThreadedChannel):
    type: Literal[15]
    default_forum_layout: NotRequired[ForumLayout]  # Defaults to 0


class CategoryChannel(_BaseGuildChannel):
    type: Literal[4]


VideoQualityMode = Literal[1, 2]


class _BaseVoiceChannel(_BaseGuildChannel, _MessageableChannel):
    rtc_region: NotRequired[str | None]
    video_quality_mode: NotRequired[VideoQualityMode]
    bitrate: int
    user_limit: int


class VoiceChannel(_BaseVoiceChannel):
    type: Literal[2]


class StageChannel(_BaseVoiceChannel):
    topic: str | None
    type: Literal[13]


PrivacyLevel = Literal[2]  # GUILD_ONLY


class StageInstance(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    channel_id: Snowflake
    topic: str
    privacy_level: PrivacyLevel
    guild_scheduled_event_id: Snowflake | None


GuildChannel = (
    TextChannel
    | NewsChannel
    | VoiceChannel
    | CategoryChannel
    | StageChannel
    | Thread
    | ForumChannel
    | MediaChannel
)


class _BasePrivateChannel(_BaseChannel):
    """Base type for private (DM) channels"""

    last_message_id: Snowflake | None
    recipients: list[User]
    last_pin_timestamp: NotRequired[str | None]


class DMChannel(_BasePrivateChannel):
    type: Literal[1]


class GroupDMChannel(_BasePrivateChannel):
    type: Literal[3]
    icon: str | None
    owner_id: Snowflake
    name: str | None
    application_id: NotRequired[Snowflake]
    managed: NotRequired[bool]


Channel = GuildChannel | DMChannel | GroupDMChannel


RequestChannelInfoField = Literal["status", "voice_start_time"]
