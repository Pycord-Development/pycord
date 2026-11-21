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

from typing import TYPE_CHECKING, Any, Literal, TypedDict

from typing_extensions import NotRequired

from .appinfo import ApplicationInfo
from .audit_log import AuditLogEntry
from .automod import AutoModRule
from .channel import Channel, StageInstance, Thread
from .guild import (
    AgeRestrictionLevel,
    DefaultMessageNotificationLevel,
    ExplicitContentFilterLevel,
    Guild,
    GuildFeature,
    IncidentsData,
    MFALevel,
    PremiumTier,
    UnavailableGuild,
    VerificationLevel,
)
from .integration import IntegrationAccount, IntegrationExpireBehavior, IntegrationType
from .interactions import ApplicationCommandPermissions, Interaction
from .member import Member
from .message import Message
from .monetization import Entitlement, Subscription
from .scheduled_events import ScheduledEvent
from .soundboard import SoundboardSound
from .thread import ThreadMember
from .user import User
from .voice import PartialVoiceState, VoiceState
from .welcome_screen import WelcomeScreen

if TYPE_CHECKING:
    from .activity import Activity, ClientStatus, StatusType
    from .appinfo import PartialApplicationInfo
    from .automod import AutoModAction, AutoModTriggerType
    from .channel import ChannelType
    from .collectibles import AvatarDecoration, Collectibles
    from .emoji import Emoji, PartialEmoji
    from .invite import InviteTargetType
    from .member import PartialMember, UserWithMember
    from .message import ReactionType
    from .role import Role
    from .snowflake import Snowflake
    from .sticker import Sticker
    from .thread import ThreadType
    from .user import PartialUser

# MISC
opcodes = Literal[
    0,  # DISPATCH
    1,  # HEARTBEAT
    2,  # IDENTIFY
    3,  # PRESENCE UPDATE
    4,  # VOICE STATE UPDATE
    6,  # RESUME
    7,  # RECONNECT
    8,  # REQUEST GUILD MEMBERS
    9,  # INVALID SESSION
    10,  # HELLO
    11,  # HEARTBEAT ACK
    31,  # REQUEST SOUNDBOARD SOUNDS
    43,  # REQUEST CHANNEL INFO
]

# APPLICATION COMMAND EVENTS

ApplicationCommandPermissionsUpdate = ApplicationCommandPermissions

# AUTO MODERATION UPDATES

AutoModerationRuleCreateEvent = AutoModRule

AutoModerationRuleUpdateEvent = AutoModRule

AutoModerationRuleDeleteEvent = AutoModRule


class AutoModActionExecutionEvent(TypedDict):
    guild_id: Snowflake
    action: AutoModAction
    rule_id: Snowflake
    rule_trigger_type: AutoModTriggerType
    user_id: Snowflake
    channel_id: NotRequired[Snowflake]
    message_id: NotRequired[Snowflake]
    alert_system_message_id: NotRequired[Snowflake]
    content: str  # Needs message intent
    matched_keyword: str | None
    matched_content: str | None  # Needs message intent


# CHANNEL EVENTS

ChannelCreateEvent = Channel

ChannelUpdateEvent = Channel

ChannelDeleteEvent = Channel


class ChannelInfoChannel(TypedDict):
    id: Snowflake
    status: NotRequired[str | None]
    voice_start_time: NotRequired[int | None]


class ChannelInfoEvent(TypedDict):
    guild_id: Snowflake
    channels: list[ChannelInfoChannel]


class VoiceChannelStatusUpdateEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    status: str | None


class VoiceChannelStartTimeUpdateEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    voice_start_time: NotRequired[int | None]


class ThreadCreateEvent(Thread):
    """One of these will be present, see https://docs.discord.com/developers/events/gateway-events#thread-create"""

    newly_created: NotRequired[bool]
    member: NotRequired[ThreadMember]


ThreadUpdateEvent = Thread


class ThreadDeleteEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    parent_id: Snowflake
    type: ThreadType


class ThreadListSyncEvent(TypedDict):
    guild_id: Snowflake
    channel_ids: NotRequired[list[Snowflake]]
    threads: list[Thread]
    members: list[ThreadMember]


class ThreadMemberUpdateEvent(ThreadMember):
    guild_id: Snowflake


class ThreadMembersUpdateEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    member_count: int  # Capped at 50
    added_members: NotRequired[list[ThreadMember]]
    removed_member_ids: NotRequired[list[Snowflake]]


class ChannelPinsUpdateEvent(TypedDict):
    guild_id: NotRequired[Snowflake]
    channel_id: Snowflake
    last_pin_timestamp: NotRequired[str | None]


# ENTITLEMENT EVENTS


EntitlementCreateEvent = Entitlement

EntitlementUpdateEvent = Entitlement

EntitlementDeleteEvent = Entitlement

# GUILD EVENTS


class _GuildCreateGuild(TypedDict):
    """The full version of the guild object sent during GUILD_CREATE, including extra fields"""

    name: str
    icon: str | None
    icon_hash: NotRequired[str | None]
    splash: str | None
    discovery_splash: str | None
    owner: NotRequired[bool]
    owner_id: Snowflake
    permissions: NotRequired[str]
    afk_channel_id: Snowflake | None
    afk_timeout: int
    widget_enabled: NotRequired[bool]
    widget_channel_id: NotRequired[Snowflake | None]
    verification_level: VerificationLevel
    default_message_notifications: DefaultMessageNotificationLevel
    explicit_content_filter: ExplicitContentFilterLevel
    roles: list[Role]
    emojis: list[Emoji]
    features: list[GuildFeature]
    mfa_level: MFALevel
    application_id: Snowflake | None
    system_channel_id: Snowflake | None
    system_channel_flags: int
    rules_channel_id: Snowflake | None
    max_presences: NotRequired[int | None]
    max_members: NotRequired[int]
    vanity_url_code: str | None
    description: str | None
    banner: str | None
    premium_tier: PremiumTier
    premium_subscription_count: NotRequired[int]
    preferred_locale: str
    public_updates_channel_id: Snowflake | None
    max_video_channel_users: NotRequired[int]
    max_stage_video_channel_users: NotRequired[int]
    welcome_screen: NotRequired[WelcomeScreen]
    nsfw_level: AgeRestrictionLevel
    stickers: NotRequired[list[Sticker]]
    premium_progress_bar_enabled: NotRequired[bool]
    safety_alerts_channel_id: Snowflake | None
    incidents_data: IncidentsData | None
    guild_scheduled_events: NotRequired[list[ScheduledEvent]]
    # extra fields for this event below. Duplicated because of redefining required fields

    joined_at: str
    large: bool
    unavailable: NotRequired[bool]
    member_count: int
    voice_states: list[PartialVoiceState]
    members: list[Member]
    channels: list[Channel]
    threads: list[Thread]
    presences: list[PresenceUpdateEvent]


GuildCreateEvent = _GuildCreateGuild | UnavailableGuild

GuildUpdateEvent = Guild

GuildDeleteEvent = UnavailableGuild


class AuditLogEntryCreateEvent(AuditLogEntry):
    guild_id: Snowflake


class BanAddEvent(TypedDict):
    guild_id: Snowflake
    user: User


class BanRemoveEvent(TypedDict):
    guild_id: Snowflake
    user: User


class GuildEmojisUpdateEvent(TypedDict):
    guild_id: Snowflake
    emojis: list[Emoji]


class GuildStickersUpdateEvent(TypedDict):
    guild_id: Snowflake
    stickers: list[Sticker]


class GuildIntegrationsUpdateEvent(TypedDict):
    guild_id: Snowflake


class GuildMemberAddEvent(Member):
    guild_id: Snowflake


class GuildMemberRemoveEvent(TypedDict):
    guild_id: Snowflake
    user: User


class GuildMemberUpdateEvent(TypedDict):
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


class GuildMembersChunkEvent(TypedDict):
    guild_id: Snowflake
    members: list[Member]
    chunk_index: int
    chunk_count: int
    not_found: NotRequired[list[Snowflake]]
    presences: NotRequired[list[PresenceUpdateEvent]]
    nonce: NotRequired[str]


class RoleCreateEvent(TypedDict):
    guild_id: Snowflake
    role: Role


RoleUpdateEvent = RoleCreateEvent


class RoleDeleteEvent(TypedDict):
    guild_id: Snowflake
    role_id: Snowflake


ScheduledEventCreateEvent = ScheduledEvent

ScheduledEventUpdateEvent = ScheduledEvent

ScheduledEventDeleteEvent = ScheduledEvent

ScheduledEventEvent = (
    ScheduledEventCreateEvent | ScheduledEventUpdateEvent | ScheduledEventDeleteEvent
)


class ScheduledEventUserAddEvent(TypedDict):
    guild_scheduled_event_id: Snowflake
    user_id: Snowflake
    guild_id: Snowflake


ScheduledEventUserRemoveEvent = ScheduledEventUserAddEvent

SoundboardSoundCreateEvent = SoundboardSound

SoundboardSoundUpdateEvent = SoundboardSound


class SoundboardSoundDeleteEvent(TypedDict):
    sound_id: Snowflake
    guild_id: Snowflake


class SoundboardSoundsUpdateEvent(TypedDict):
    soundboard_sounds: list[SoundboardSound]
    guild_id: Snowflake


class SoundboardSoundsEvent(TypedDict):
    """Sent in response to requesting soundboard sounds"""

    soundboard_sounds: list[SoundboardSound]
    guild_id: Snowflake


# INTEGRATION EVENTS


class IntegrationCreateEvent(TypedDict):
    id: Snowflake
    name: str
    type: IntegrationType
    enabled: bool
    syncing: NotRequired[bool]
    role_id: NotRequired[Snowflake]
    enable_emoticons: NotRequired[bool]
    expire_behavior: NotRequired[IntegrationExpireBehavior]
    expire_grace_period: NotRequired[int]
    account: IntegrationAccount
    synced_at: NotRequired[str]
    subscriber_count: NotRequired[int]
    revoked: NotRequired[bool]
    application: NotRequired[ApplicationInfo]
    # extra field for this event
    guild_id: Snowflake


IntegrationUpdateEvent = IntegrationCreateEvent


class IntegrationDeleteEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    application_id: NotRequired[Snowflake]


# INVITE EVENTS


class InviteCreateEvent(TypedDict):
    channel_id: Snowflake
    code: str
    created_at: str
    guild_id: NotRequired[Snowflake]
    inviter: NotRequired[User]
    max_age: int
    max_uses: int
    target_type: NotRequired[InviteTargetType]
    target_user: NotRequired[PartialUser]
    target_application: NotRequired[PartialApplicationInfo]
    temporary: bool
    uses: int
    expires_at: str | None
    role_ids: NotRequired[list[Snowflake]]


class InviteDeleteEvent(TypedDict):
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]
    code: str


GatewayInviteEvent = InviteCreateEvent | InviteDeleteEvent

# MESSAGE EVENTS


class MessageCreateEvent(Message):
    guild_id: NotRequired[Snowflake]
    member: NotRequired[PartialMember]
    mentions: list[UserWithMember]
    channel_type: NotRequired[ChannelType]


MessageUpdateEvent = MessageCreateEvent


class MessageDeleteEvent(TypedDict):
    id: Snowflake
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]


class BulkMessageDeleteEvent(TypedDict):
    ids: list[Snowflake]
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]


class ReactionAddEvent(TypedDict):
    user_id: Snowflake
    channel_id: Snowflake
    message_id: Snowflake
    guild_id: NotRequired[Snowflake]
    member: NotRequired[Member]
    emoji: PartialEmoji
    message_author_id: NotRequired[Snowflake]
    burst: bool
    burst_colors: NotRequired[list[str]]
    type: int


class ReactionRemoveEvent(TypedDict):
    user_id: Snowflake
    channel_id: Snowflake
    message_id: Snowflake
    guild_id: NotRequired[Snowflake]
    emoji: PartialEmoji
    burst: bool
    type: ReactionType


class ReactionClearEvent(TypedDict):
    channel_id: Snowflake
    message_id: Snowflake
    guild_id: NotRequired[Snowflake]


class ReactionClearEmojiEvent(TypedDict):
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]
    message_id: Snowflake
    emoji: PartialEmoji


# PRESENCE UPDATES


class PresenceUpdateEvent(TypedDict):
    """The presence update *can* always be partial in that it contains a user with at least the id"""

    user: PartialUser
    guild_id: Snowflake
    status: StatusType
    activities: list[Activity]
    client_status: ClientStatus


class TypingStartEvent(TypedDict):
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]
    user_id: Snowflake
    timestamp: int
    member: NotRequired[Member]


UserUpdateEvent = User


# VOICE EVENTS


class VoiceChannelEffectSendEvent(TypedDict):
    channel_id: Snowflake
    guild_id: Snowflake
    user_id: Snowflake
    emoji: NotRequired[PartialEmoji | None]
    animation_type: NotRequired[int | None]
    animation_id: NotRequired[int]
    sound_id: NotRequired[Snowflake | int]
    sound_volume: NotRequired[float]


VoiceStateUpdateEvent = VoiceState


class VoiceServerUpdateEvent(TypedDict):
    token: str
    guild_id: Snowflake
    endpoint: str | None


# WEBHOOK EVENTS


class WebhooksUpdateEvent(TypedDict):
    guild_id: Snowflake
    channel_id: Snowflake


# INTERACTION EVENTS

InteractionCreateEvent = Interaction

# STAGE EVENTS

StageInstanceCreateEvent = StageInstance

StageInstanceUpdateEvent = StageInstance

StageInstanceDeleteEvent = StageInstance

# SUBSCRIPTION EVENTS

SubscriptionCreateEvent = Subscription

SubscriptionUpdateEvent = Subscription

SubscriptionDeleteEvent = Subscription

# POLL EVENTS


class MessagePollVoteAddEvent(TypedDict):
    user_id: Snowflake
    channel_id: Snowflake
    message_id: Snowflake
    guild_id: NotRequired[Snowflake]
    answer_id: int


class MessagePollVoteRemoveEvent(TypedDict):
    user_id: Snowflake
    channel_id: Snowflake
    message_id: Snowflake
    guild_id: NotRequired[Snowflake]
    answer_id: int


MessagePollVoteEvent = MessagePollVoteAddEvent | MessagePollVoteRemoveEvent


# RATE LIMIT EVENTS


class RatelimitedEvent(TypedDict):
    opcode: opcodes
    retry_after: float
    meta: Any  # pyright: ignore[reportExplicitAny] Very obscurely documented
