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

from .._typed_dict import NotRequired, Required, TypedDict
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
    "ANIMATED_BANNER",
    "ANIMATED_ICON",
    "APPLICATION_COMMAND_PERMISSIONS_V2",
    "AUTO_MODERATION",
    "BANNER",
    "CHANNEL_BANNER",
    "COMMERCE",
    "COMMUNITY",
    "DEVELOPER_SUPPORT_SERVER",
    "DISCOVERABLE",
    "FEATURABLE",
    "HAS_DIRECTORY_ENTRY",
    "HUB",
    "INTERNAL_EMPLOYEE_ONLY",
    "INVITES_DISABLED",
    "INVITE_SPLASH",
    "LINKED_TO_HUB",
    "MEMBER_PROFILES",
    "MEMBER_VERIFICATION_GATE_ENABLED",
    "MONETIZATION_ENABLED",
    "MORE_EMOJI",
    "MORE_STICKERS",
    "NEWS",
    "NEW_THREAD_PERMISSIONS",
    "PARTNERED",
    "PREMIUM_TIER_3_OVERRIDE",
    "PREVIEW_ENABLED",
    "ROLE_ICONS",
    "ROLE_SUBSCRIPTIONS_ENABLED",
    "SEVEN_DAY_THREAD_ARCHIVE",
    "TEXT_IN_VOICE_ENABLED",
    "THREAD_DEFAULT_AUTO_ARCHIVE_DURATION",
    "THREADS_ENABLED_TESTING",
    "THREE_DAY_THREAD_ARCHIVE",
    "TICKETED_EVENTS_ENABLED",
    "VANITY_URL",
    "VERIFIED",
    "VIP_REGIONS",
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
