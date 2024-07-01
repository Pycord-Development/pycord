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

from typing import TYPE_CHECKING, Literal

from .channel import ChannelType
from .components import Component
from .embed import Embed
from .emoji import PartialEmoji
from .member import Member, UserWithMember
from .poll import Poll
from .snowflake import Snowflake, SnowflakeList
from .sticker import StickerItem
from .threads import Thread
from .user import User

if TYPE_CHECKING:
    from .interactions import InteractionMetadata, MessageInteraction

from .._typed_dict import NotRequired, TypedDict


class ChannelMention(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    type: ChannelType
    name: str


class Reaction(TypedDict):
    count: int
    me: bool
    emoji: PartialEmoji
    burst: bool
    me_burst: bool
    burst_colors: list[str]
    count_details: ReactionCountDetails


class ReactionCountDetails(TypedDict):
    normal: int
    burst: int


class Attachment(TypedDict):
    height: NotRequired[int | None]
    width: NotRequired[int | None]
    content_type: NotRequired[str]
    description: NotRequired[str]
    spoiler: NotRequired[bool]
    id: Snowflake
    filename: str
    size: int
    url: str
    proxy_url: str
    duration_secs: NotRequired[float]
    waveform: NotRequired[str]
    flags: NotRequired[int]
    title: NotRequired[str]


MessageActivityType = Literal[1, 2, 3, 5]


class MessageActivity(TypedDict):
    type: MessageActivityType
    party_id: str


class MessageApplication(TypedDict):
    cover_image: NotRequired[str]
    id: Snowflake
    description: str
    icon: str | None
    name: str


class MessageReference(TypedDict, total=False):
    message_id: Snowflake
    channel_id: Snowflake
    guild_id: Snowflake
    fail_if_not_exists: bool


MessageType = Literal[
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 18, 19, 20, 21, 22, 23, 24
]


class Message(TypedDict):
    guild_id: NotRequired[Snowflake]
    member: NotRequired[Member]
    mention_channels: NotRequired[list[ChannelMention]]
    reactions: NotRequired[list[Reaction]]
    nonce: NotRequired[int | str]
    webhook_id: NotRequired[Snowflake]
    activity: NotRequired[MessageActivity]
    application: NotRequired[MessageApplication]
    application_id: NotRequired[Snowflake]
    message_reference: NotRequired[MessageReference]
    flags: NotRequired[int]
    sticker_items: NotRequired[list[StickerItem]]
    referenced_message: NotRequired[Message | None]
    interaction: NotRequired[MessageInteraction]
    interaction_metadata: NotRequired[InteractionMetadata]
    components: NotRequired[list[Component]]
    thread: NotRequired[Thread | None]
    id: Snowflake
    channel_id: Snowflake
    author: User
    content: str
    timestamp: str
    edited_timestamp: str | None
    tts: bool
    mention_everyone: bool
    mentions: list[UserWithMember]
    mention_roles: SnowflakeList
    attachments: list[Attachment]
    embeds: list[Embed]
    pinned: bool
    type: MessageType
    poll: Poll


AllowedMentionType = Literal["roles", "users", "everyone"]


class AllowedMentions(TypedDict):
    parse: list[AllowedMentionType]
    roles: SnowflakeList
    users: SnowflakeList
    replied_user: bool


class MessageCall(TypedDict):
    participants: SnowflakeList
    ended_timestamp: NotRequired[str]
