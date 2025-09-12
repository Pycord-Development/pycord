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

from typing_extensions import NotRequired, Required, TypedDict

from .activity import PartialPresenceUpdate
from .channel import GuildChannel
from .emoji import Emoji
from .member import Member
from .role import Role
from .scheduled_events import ScheduledEvent
from .snowflake import Snowflake
from .threads import Thread
from .user import User
from .voice import GuildVoiceState
from .welcome_screen import WelcomeScreen


class Ban(TypedDict):
    reason: str | None
    user: User


class UnavailableGuild(TypedDict):
    unavailable: NotRequired[bool]
    id: Snowflake


DefaultMessageNotificationLevel = Literal[0, 1]
ExplicitContentFilterLevel = Literal[0, 1, 2]
MFALevel = Literal[0, 1]
VerificationLevel = Literal[0, 1, 2, 3, 4]
NSFWLevel = Literal[0, 1, 2, 3]
PremiumTier = Literal[0, 1, 2, 3]
GuildFeature = Literal[
    "ACTIVITIES_ALPHA",
    "ACTIVITIES_EMPLOYEE",
    "ACTIVITIES_INTERNAL_DEV",
    "ACTIVITY_FEED_DISABLED_BY_USER",
    "ACTIVITY_FEED_ENABLED_BY_USER",
    "AGE_VERIFICATION_LARGE_GUILD",
    "ANIMATED_BANNER",
    "ANIMATED_ICON",
    "APPLICATION_COMMAND_PERMISSIONS_V2",
    "AUDIO_BITRATE_128_KBPS",
    "AUDIO_BITRATE_256_KBPS",
    "AUDIO_BITRATE_384_KBPS",
    "AUTOMOD_TRIGGER_KEYWORD_FILTER",
    "AUTOMOD_TRIGGER_ML_SPAM_FILTER",
    "AUTOMOD_TRIGGER_SPAM_LINK_FILTER",
    "AUTOMOD_TRIGGER_USER_PROFILE",
    "AUTO_MODERATION",
    "BANNER",
    "BFG",
    "BOOSTING_TIERS_EXPERIMENT_MEDIUM_GUILD",
    "BOOSTING_TIERS_EXPERIMENT_SMALL_GUILD",
    "BOT_DEVELOPER_EARLY_ACCESS",
    "BURST_REACTIONS",
    "CHANNEL_BANNER",
    "CHANNEL_EMOJIS_GENERATED",
    "CHANNEL_HIGHLIGHTS",
    "CHANNEL_HIGHLIGHTS_DISABLED",
    "CHANNEL_ICON_EMOJIS_GENERATED",
    "CLAN",
    "CLAN_DISCOVERY_DISABLED",
    "CLAN_PILOT_GENSHIN",
    "CLAN_PILOT_VALORANT",
    "CLAN_SAFETY_REVIEW_DISABLED",
    "CLYDE_DISABLED",
    "CLYDE_ENABLED",
    "CLYDE_EXPERIMENT_ENABLED",
    "COMMERCE",
    "COMMUNITY",
    "COMMUNITY_CANARY",
    "COMMUNITY_EXP_LARGE_GATED",
    "COMMUNITY_EXP_LARGE_UNGATED",
    "COMMUNITY_EXP_MEDIUM",
    "CREATOR_ACCEPTED_NEW_TERMS",
    "CREATOR_MONETIZABLE",
    "CREATOR_MONETIZABLE_DISABLED",
    "CREATOR_MONETIZABLE_PENDING_NEW_OWNER_ONBOARDING",
    "CREATOR_MONETIZABLE_PROVISIONAL",
    "CREATOR_MONETIZABLE_RESTRICTED",
    "CREATOR_MONETIZABLE_WHITEGLOVE",
    "CREATOR_MONETIZATION_APPLICATION_ALLOWLIST",
    "CREATOR_STORE_PAGE",
    "DEVELOPER_SUPPORT_SERVER",
    "DISCOVERABLE",
    "DISCOVERABLE_DISABLED",
    "ENABLED_DISCOVERABLE_BEFORE",
    "ENABLED_MODERATION_EXPERIENCE_FOR_NON_COMMUNITY",
    "ENHANCED_ROLE_COLORS",
    "EXPOSED_TO_ACTIVITIES_WTP_EXPERIMENT",
    "EXPOSED_TO_BOOSTING_TIERS_EXPERIMENT",
    "FEATURABLE",
    "FORCE_RELAY",
    "FORWARDING_DISABLED",
    "GAME_SERVER_HOSTING",
    "GENSHIN_L30",
    "GUESTS_ENABLED",
    "GUILD_AUTOMOD_DEFAULT_LIST",
    "GUILD_COMMUNICATION_DISABLED_GUILDS",
    "GUILD_HOME_DEPRECATION_OVERRIDE",
    "GUILD_HOME_OVERRIDE",
    "GUILD_HOME_TEST",
    "GUILD_MEMBER_VERIFICATION_EXPERIMENT",
    "GUILD_ONBOARDING",
    "GUILD_ONBOARDING_ADMIN_ONLY",
    "GUILD_ONBOARDING_EVER_ENABLED",
    "GUILD_ONBOARDING_HAS_PROMPTS",
    "GUILD_PRODUCTS",
    "GUILD_PRODUCTS_ALLOW_ARCHIVED_FILE",
    "GUILD_ROLE_SUBSCRIPTIONS",
    "GUILD_ROLE_SUBSCRIPTION_PURCHASE_FEEDBACK_LOOP",
    "GUILD_ROLE_SUBSCRIPTION_TIER_TEMPLATE",
    "GUILD_ROLE_SUBSCRIPTION_TRIALS",
    "GUILD_SERVER_GUIDE",
    "GUILD_TAGS",
    "GUILD_TAGS_BADGE_PACK_FLEX",
    "GUILD_TAGS_BADGE_PACK_PETS",
    "GUILD_WEB_PAGE_VANITY_URL",
    "HAD_EARLY_ACTIVITIES_ACCESS",
    "HAS_DIRECTORY_ENTRY",
    "HIDE_FROM_EXPERIMENT_UI",
    "HUB",
    "INCREASED_THREAD_LIMIT",
    "INTERNAL_EMPLOYEE_ONLY",
    "INVITES_DISABLED",
    "INVITE_SPLASH",
    "LEADERBOARD_ENABLED",
    "LINKED_TO_HUB",
    "LURKABLE",
    "MARKETPLACES_CONNECTION_ROLES",
    "MAX_FILE_SIZE_100_MB",
    "MAX_FILE_SIZE_50_MB",
    "MEMBER_LIST_DISABLED",
    "MEMBER_PROFILES",
    "MEMBER_SAFETY_PAGE_ROLLOUT",
    "MEMBER_VERIFICATION_GATE_ENABLED",
    "MEMBER_VERIFICATION_MANUAL_APPROVAL",
    "MEMBER_VERIFICATION_ROLLOUT_TEST",
    "MOBILE_WEB_ROLE_SUBSCRIPTION_PURCHASE_PAGE",
    "MONETIZATION_ENABLED",
    "MORE_EMOJI",
    "MORE_SOUNDBOARD",
    "MORE_STICKERS",
    "NEWS",
    "NEW_THREAD_PERMISSIONS",
    "NON_COMMUNITY_RAID_ALERTS",
    "PARTNERED",
    "PIN_PERMISSION_MIGRATION_COMPLETE",
    "PREMIUM_TIER_3_OVERRIDE",
    "PREVIEW_ENABLED",
    "PRIVATE_THREADS",
    "PRODUCTS_AVAILABLE_FOR_PURCHASE",
    "PUBLIC",
    "PUBLIC_DISABLED",
    "RAID_ALERTS_DISABLED",
    "RAID_ALERTS_ENABLED",
    "RAPIDASH_TEST",
    "RAPIDASH_TEST_REBIRTH",
    "RELAY_ENABLED",
    "REPORT_TO_MOD_PILOT",
    "REPORT_TO_MOD_SURVEY",
    "RESTRICT_SPAM_RISK_GUILDS",
    "ROLE_ICONS",
    "ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE",
    "ROLE_SUBSCRIPTIONS_ENABLED",
    "ROLE_SUBSCRIPTIONS_ENABLED_FOR_PURCHASE",
    "SERVER_PROFILES_TEST",
    "SEVEN_DAY_THREAD_ARCHIVE",
    "SHARD",
    "SHARED_CANVAS_FRIENDS_AND_FAMILY_TEST",
    "SOUNDBOARD",
    "STAGE_CHANNEL_VIEWERS_150",
    "STAGE_CHANNEL_VIEWERS_300",
    "STAGE_CHANNEL_VIEWERS_50",
    "SUMMARIES_DISABLED_BY_USER",
    "SUMMARIES_ENABLED",
    "SUMMARIES_ENABLED_BY_USER",
    "SUMMARIES_ENABLED_GA",
    "SUMMARIES_LONG_LOOKBACK",
    "SUMMARIES_OPT_OUT_EXPERIENCE",
    "TEXT_IN_STAGE_ENABLED",
    "TEXT_IN_VOICE_ENABLED",
    "THREADS_ENABLED",
    "THREADS_ENABLED_TESTING",
    "THREADS_ONLY_CHANNEL",
    "THREAD_DEFAULT_AUTO_ARCHIVE_DURATION",
    "THREE_DAY_THREAD_ARCHIVE",
    "TICKETED_EVENTS_ENABLED",
    "TICKETING_ENABLED",
    "TIERLESS_BOOSTING",
    "TIERLESS_BOOSTING_CLIENT_TEST",
    "TIERLESS_BOOSTING_SYSTEM_MESSAGE",
    "TIERLESS_BOOSTING_TEST",
    "VALORANT_L30",
    "VANITY_URL",
    "VERIFIED",
    "VIDEO_BITRATE_ENHANCED",
    "VIDEO_QUALITY_1080_60FPS",
    "VIDEO_QUALITY_720_60FPS",
    "VIP_REGIONS",
    "VOICE_CHANNEL_EFFECTS",
    "VOICE_IN_THREADS",
    "WELCOME_SCREEN_ENABLED",
]


class _BaseGuildPreview(UnavailableGuild):
    name: str
    icon: str | None
    splash: str | None
    discovery_splash: str | None
    emojis: list[Emoji]
    features: list[GuildFeature]
    description: str | None


class _GuildPreviewUnique(TypedDict):
    approximate_member_count: int
    approximate_presence_count: int


class GuildPreview(_BaseGuildPreview, _GuildPreviewUnique):
    pass


class Guild(_BaseGuildPreview):
    icon_hash: NotRequired[str | None]
    owner: NotRequired[bool]
    permissions: NotRequired[str]
    widget_enabled: NotRequired[bool]
    widget_channel_id: NotRequired[Snowflake | None]
    joined_at: NotRequired[str | None]
    large: NotRequired[bool]
    member_count: NotRequired[int]
    voice_states: NotRequired[list[GuildVoiceState]]
    members: NotRequired[list[Member]]
    channels: NotRequired[list[GuildChannel]]
    presences: NotRequired[list[PartialPresenceUpdate]]
    threads: NotRequired[list[Thread]]
    max_presences: NotRequired[int | None]
    max_members: NotRequired[int]
    premium_subscription_count: NotRequired[int]
    premium_progress_bar_enabled: NotRequired[bool]
    max_video_channel_users: NotRequired[int]
    guild_scheduled_events: NotRequired[list[ScheduledEvent]]
    owner_id: Snowflake
    afk_channel_id: Snowflake | None
    afk_timeout: int
    verification_level: VerificationLevel
    default_message_notifications: DefaultMessageNotificationLevel
    explicit_content_filter: ExplicitContentFilterLevel
    roles: list[Role]
    mfa_level: MFALevel
    nsfw_level: NSFWLevel
    application_id: Snowflake | None
    system_channel_id: Snowflake | None
    system_channel_flags: int
    rules_channel_id: Snowflake | None
    vanity_url_code: str | None
    banner: str | None
    premium_tier: PremiumTier
    preferred_locale: str
    public_updates_channel_id: Snowflake | None


class InviteGuild(Guild, total=False):
    welcome_screen: WelcomeScreen


class GuildWithCounts(Guild, _GuildPreviewUnique):
    pass


class GuildPrune(TypedDict):
    pruned: int | None


class ChannelPositionUpdate(TypedDict):
    id: Snowflake
    position: int | None
    lock_permissions: bool | None
    parent_id: Snowflake | None


class RolePositionUpdate(TypedDict, total=False):
    id: Required[Snowflake]
    position: Snowflake | None


class GuildMFAModify(TypedDict):
    level: Literal[0, 1]


class GuildBulkBan(TypedDict):
    banned_users: list[Snowflake]
    failed_users: list[Snowflake]
