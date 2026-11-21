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
    from .channel import Thread
    from .emoji import Emoji
    from .events import PresenceUpdateEvent
    from .role import Role
    from .scheduled_events import ScheduledEvent
    from .snowflake import Snowflake
    from .sticker import Sticker
    from .user import User
    from .welcome_screen import WelcomeScreen


class Ban(TypedDict):
    reason: str | None
    user: User


DefaultMessageNotificationLevel = Literal[
    0,  # ALL_MESSAGES
    1,  # ONLY_MENTIONS
]
ExplicitContentFilterLevel = Literal[
    0,  # DISABLED
    1,  # MEMBERS_WITHOUT_ROLES
    2,  # ALL_MEMBERS
]
MFALevel = Literal[
    0,  # NONE
    1,  # ELEVATED
]
VerificationLevel = Literal[
    0,  # NONE
    1,  # LOW
    2,  # MEDIUM
    3,  # HIGH
    4,  # VERY HIGH
]
AgeRestrictionLevel = Literal[
    0,  # DEFAULT
    1,  # EXPLICIT
    2,  # SAFE
    3,  # AGE_RESTRICTED
]
PremiumTier = Literal[
    0,  # DEFAULT
    1,  # TIER_1
    2,  # TIER_2
    3,  # TIER_3
]
GuildFeature = Literal[  # All guild features, including ones that cannot be modified
    "ANIMATED_BANNER",
    "ANIMATED_ICON",
    "APPLICATION_COMMAND_PERMISSIONS_V2",
    "AUTO_MODERATION",
    "BANNER",
    "COMMUNITY",
    "CREATOR_MONETIZABLE_PROVISIONAL",
    "CREATOR_STORE_PAGE",
    "DEVELOPER_SUPPORT_SERVER",
    "DISCOVERABLE",
    "ENHANCED_ROLE_COLORS",
    "FEATURABLE",
    "GUILD_TAGS",
    "GUESTS_ENABLED",
    "INVITES_DISABLED",
    "INVITE_SPLASH",
    "MEMBER_VERIFICATION_GATE_ENABLED",
    "MORE_SOUNDBOARD",
    "MORE_STICKERS",
    "NEWS",
    "PARTNERED",
    "PREVIEW_ENABLED",
    "PRUNE_REQUIRES_ADMIN",
    "RAID_ALERTS_DISABLED",
    "ROLE_ICONS",
    "ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE",
    "ROLE_SUBSCRIPTIONS_ENABLED",
    "SOUNDBOARD",
    "TICKETED_EVENTS_ENABLED",
    "VANITY_URL",
    "VERIFIED",
    "VIP_REGIONS",
    "WELCOME_SCREEN_ENABLED",
]

MutableGuildFeature = Literal[  # All guild features that can be modified
    "COMMUNITY",
    "DISCOVERABLE",
    "INVITES_DISABLED",
    "RAID_ALERTS_DISABLED",
]


class GuildTrait(TypedDict):
    """A trait shown on an guild's invite popup"""

    emoji_id: Snowflake | None
    emoji_name: str | None
    emoji_animated: bool
    label: str
    position: int


GuildVisibilityLevel = Literal[
    1,  # PUBLIC
    2,  # RESTRICTED
    3,  # PUBLIC_WITH_RECRUITMENT
]


class UnavailableGuild(TypedDict):
    """A partial guild object for an offline guild, or a guild whose info wasn't passed through the gateway during gateway connection"""

    id: Snowflake
    unavailable: NotRequired[bool]


class GuildPreview(UnavailableGuild):
    name: str
    icon: str | None
    splash: str | None
    discovery_splash: str | None
    emojis: list[Emoji]
    features: list[GuildFeature]
    approximate_member_count: int
    approximate_presence_count: int
    description: str | None
    stickers: list[Sticker]


class Guild(UnavailableGuild):
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
    premium_progress_bar_enabled: bool
    safety_alerts_channel_id: Snowflake | None
    incidents_data: IncidentsData | None
    presences: NotRequired[list[PresenceUpdateEvent]]
    threads: NotRequired[list[Thread]]
    guild_scheduled_events: NotRequired[list[ScheduledEvent]]


class GuildWithCounts(Guild):
    """A guild object when it `with_counts` has been passed"""

    approximate_member_count: int
    approximate_presence_count: int


class InviteGuild(Guild):
    welcome_screen: NotRequired[WelcomeScreen]


class GuildPruneCount(TypedDict):
    """Returned when getting the guild prune count. Number of members that would be kicked in a prune"""

    pruned: int | None


class ChannelPositionUpdate(TypedDict):
    """The allowed fields for an entry in the PATCH request to modify guild channel positions. Only one entry in the
    request is allowed to change parent_id
    """

    id: Snowflake
    position: NotRequired[int | None]
    lock_permissions: NotRequired[bool | None]
    parent_id: NotRequired[Snowflake | None]


class RolePositionUpdate(TypedDict):
    """The allowed fields for an entry in the PATCH request to modify guild role positions."""

    id: Snowflake
    position: NotRequired[int | None]


class GuildMFAModify(TypedDict):
    level: MFALevel


class GuildBulkBan(TypedDict):
    """The allowed fields for the POST request to make bulk guild bans"""

    user_ids: list[Snowflake]  # Max 200
    deleted_message_seconds: NotRequired[int]  # Defaults to 0


class GuildBulkBanResponse(TypedDict):
    """The response for the POST request to make bulk guild bans"""

    banned_users: list[Snowflake]
    failed_users: list[Snowflake]


class ModifyIncidents(TypedDict):
    """Allowed fields for a PATCH request to modify guild incidents"""

    invites_disabled_until: NotRequired[str | None]
    dms_disabled_until: NotRequired[str | None]


class IncidentsData(TypedDict):
    invites_disabled_until: str | None
    dms_disabled_until: str | None
    dm_spam_detected_at: NotRequired[str | None]
    raid_detected_at: NotRequired[str | None]


class GetPermissionsResponseData(TypedDict):
    """The response for the GET request to get permissions for a user or role in a guild"""

    permissions: str


class ModifyGuild(TypedDict):
    """The allowed fields for a PATCH request to modify a guild"""

    name: NotRequired[str]
    verification_level: NotRequired[VerificationLevel | None]
    default_message_notifications: NotRequired[DefaultMessageNotificationLevel | None]
    explicit_content_filter: NotRequired[ExplicitContentFilterLevel | None]
    afk_channel_id: NotRequired[Snowflake | None]
    afk_timeout: NotRequired[int]
    icon: NotRequired[str | None]
    splash: NotRequired[str | None]
    discovery_splash: NotRequired[str | None]
    banner: NotRequired[str | None]
    system_channel_id: NotRequired[Snowflake | None]
    system_channel_flags: NotRequired[int]
    rules_channel_id: NotRequired[Snowflake | None]
    public_updates_channel_id: NotRequired[Snowflake | None]
    preferred_locale: NotRequired[str | None]
    features: NotRequired[list[MutableGuildFeature]]
    description: NotRequired[str | None]
    premium_progress_bar_enabled: NotRequired[bool]
    safety_alerts_channel_id: NotRequired[Snowflake | None]
