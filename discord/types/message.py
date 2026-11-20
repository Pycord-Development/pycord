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

from docutils.parsers.rst.directives.misc import Role
from typing_extensions import NotRequired, TypedDict

from discord.message import PartialMessage

if TYPE_CHECKING:

    from .appinfo import ApplicationInfo
    from .channel import ChannelType, PartialChannel
    from .components import Component
    from .embed import Embed
    from .emoji import PartialEmoji
    from .interactions import MessageComponentInteractionMetadata, MessageInteraction
    from .member import PartialMember, UserWithMember
    from .poll import Poll
    from .shared_client_theme import SharedClientTheme
    from .snowflake import Snowflake
    from .sticker import StickerItem
    from .threads import Thread
    from .user import User


class ChannelMention(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    type: ChannelType
    name: str


class ReactionCountDetails(TypedDict):
    normal: int
    burst: int


class Reaction(TypedDict):
    count: int
    count_details: ReactionCountDetails
    me: bool
    burst: bool
    me_burst: bool
    emoji: PartialEmoji
    burst_colors: list[str]


class Attachment(TypedDict):
    id: Snowflake
    filename: str
    title: NotRequired[str]
    description: NotRequired[str]
    content_type: NotRequired[str]  # MMIME type i.e. image/png
    size: int  # Filesize in bytes
    url: str
    proxy_url: str
    height: NotRequired[int | None]
    width: NotRequired[int | None]
    placeholder: NotRequired[str]
    placeholder_version: NotRequired[int]
    ephemeral: NotRequired[bool]
    duration_secs: NotRequired[float]
    waveform: NotRequired[str]
    flags: NotRequired[int]
    clip_participants: NotRequired[User]
    clip_created_at: NotRequired[str]
    application: NotRequired[ApplicationInfo | None]


MessageActivityType = Literal[
    1,  # JOIN
    2,  # SPECTATE
    3,  # LISTEN
    5,  # JOIN_REQUEST
    6,  # STREAM_REQUEST
]


class MessageActivity(TypedDict):
    type: MessageActivityType
    party_id: NotRequired[str]


class MessageApplication(TypedDict):
    """Partial application info as part of a message object"""

    cover_image: NotRequired[str]
    id: Snowflake
    description: str
    icon: str | None
    name: str


MessageReferenceType = Literal[
    0,  # DEFAULT
    1,  # FORWARD
]


class MessageReference(TypedDict):
    type: NotRequired[MessageReferenceType]  # Will become required in the future
    message_id: NotRequired[Snowflake]
    channel_id: NotRequired[Snowflake]
    guild_id: NotRequired[Snowflake]
    fail_if_not_exists: NotRequired[bool]


MessageType = Literal[
    0,  # DEFAULT
    1,  # RECIPIENT_ADD
    2,  # RECIPIENT_REMOVE
    3,  # CALL
    4,  # CHANNEL_NAME_CHANGE
    5,  # CHANNEL_ICON_CHANGE
    6,  # CHANNEL_PINNED_MESSAGE
    7,  # USER_JOIN
    8,  # GUILD_BOOST
    9,  # GUILD_BOOST_TIER_1
    10,  # GUILD_BOOST_TIER_2
    11,  # GUILD_BOOST_TIER_3
    12,  # CHANNEL_FOLLOW_ADD
    14,  # GUILD_DISCOVERY_DISQUALIFIED
    15,  # GUILD_DISCOVERY_REQUALIFIED
    16,  # GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING
    17,  # GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING
    18,  # THREAD_CREATED
    19,  # REPLY
    20,  # CHAT_INPUT_COMMAND
    21,  # THREAD_STARTER_MESSAGE
    22,  # GUILD_INVITE_REMINDER
    23,  # CONTEXT_MENU_COMMAND
    24,  # AUTO_MODERATION_ACTION
    25,  # ROLE_SUBSCRIPTION_PURCHASE
    26,  # INTERACTION_PREMIUM_UPSELL
    27,  # STAGE_START
    28,  # STAGE_END
    29,  # STAGE_SPEAKER
    31,  # STAGE_TOPIC
    32,  # GUILD_APPLICATION_PREMIUM_SUBSCRIPTION
    36,  # GUILD_INCIDENT_ALERT_MODE_ENABLED
    37,  # GUILD_INCIDENT_ALERT_MODE_DISABLED
    38,  # GUILD_INCIDENT_REPORT_RAID
    39,  # GUILD_INCIDENT_REPORT_FALSE_ALARM
    44,  # PURCHASE_NOTIFICATION
    46,  # POLL_RESULT
]


class MessageCall(TypedDict):
    participants: list[Snowflake]
    ended_timestamp: NotRequired[str | None]


class ForwardedMessage(TypedDict):
    """A subset of fields available in a message, applies to all forwarded messages"""

    type: MessageType
    content: str
    embeds: list[Embed]
    attachments: list[Attachment]
    timestamp: str
    edited_timestamp: str | None
    flags: NotRequired[int]
    mentions: list[UserWithMember]
    mention_roles: list[Snowflake]
    sticker_items: NotRequired[list[StickerItem]]
    components: NotRequired[list[Component]]


class MessageSnapshot(TypedDict):
    message: ForwardedMessage


class RoleSubscriptionData(TypedDict):
    role_subscription_listing_id: Snowflake
    tier_name: str
    total_months_subscribed: int
    is_renewal: bool


class MessageResolvedData(TypedDict):
    users: NotRequired[dict[Snowflake, User]]
    members: NotRequired[dict[Snowflake, PartialMember]]
    roles: NotRequired[dict[Snowflake, Role]]
    channels: NotRequired[dict[Snowflake, PartialChannel]]
    messages: NotRequired[dict[Snowflake, PartialMessage]]
    attachments: NotRequired[dict[Snowflake, Attachment]]


class Message(TypedDict):
    id: Snowflake
    channel_id: Snowflake
    author: User  # May not be valid for certain message types
    content: str
    timestamp: str
    edited_timestamp: str | None
    tts: bool
    mention_everyone: bool
    mentions: list[UserWithMember]
    mention_roles: list[Snowflake]
    mention_channels: NotRequired[list[ChannelMention]]
    attachments: list[Attachment]
    embeds: list[Embed]
    reactions: NotRequired[list[Reaction]]
    nonce: NotRequired[int | str]
    pinned: bool
    webhook_id: NotRequired[Snowflake]
    type: MessageType
    activity: NotRequired[MessageActivity]
    application: NotRequired[MessageApplication]
    application_id: NotRequired[Snowflake]
    flags: NotRequired[int]
    message_reference: NotRequired[MessageReference]
    message_snapshots: NotRequired[list[MessageSnapshot]]
    referenced_message: NotRequired[Message | None]
    interaction_metadata: NotRequired[MessageComponentInteractionMetadata]
    interaction: NotRequired[MessageInteraction]
    thread: NotRequired[Thread | None]
    components: NotRequired[list[Component]]
    sticker_items: NotRequired[list[StickerItem]]
    position: NotRequired[int]
    role_subscription_data: NotRequired[RoleSubscriptionData]
    resolved: NotRequired[MessageResolvedData]
    poll: NotRequired[Poll]
    call: NotRequired[MessageCall]
    shared_client_theme: NotRequired[SharedClientTheme]


class MessagePin(TypedDict):
    pinned_at: str
    message: Message


class MessagePinPagination(TypedDict):
    """Response of a get channel pins request"""

    items: list[MessagePin]
    has_more: bool


AllowedMentionType = Literal["roles", "users", "everyone"]


class AllowedMentions(TypedDict):
    """Allowed fields for the allowed mentions object when sending a message"""

    parse: NotRequired[list[AllowedMentionType]]
    roles: NotRequired[list[Snowflake]]
    users: NotRequired[list[Snowflake]]
    replied_user: NotRequired[bool]
