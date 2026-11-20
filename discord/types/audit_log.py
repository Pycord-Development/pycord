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
    from .automod import AutoModRule
    from .channel import ChannelType, PermissionOverwrite, Thread, VideoQualityMode
    from .guild import (
        DefaultMessageNotificationLevel,
        ExplicitContentFilterLevel,
        MFALevel,
        VerificationLevel,
    )
    from .integration import IntegrationExpireBehavior, PartialIntegration
    from .interactions import ApplicationCommand
    from .role import Role
    from .scheduled_events import ScheduledEvent
    from .snowflake import Snowflake
    from .user import User
    from .webhook import Webhook

AuditLogEvent = Literal[
    1,  # GUILD_UPDATE
    10,  # CHANNEL_CREATE
    11,  # CHANNEL_UPDATE
    12,  # CHANNEL_DELETE
    13,  # CHANNEL_OVERWRITE_CREATE
    14,  # CHANNEL_OVERWRITE_UPDATE
    15,  # CHANNEL_OVERWRITE_DELETE
    16,  # CHANNEL_POSITION_UPDATE
    20,  # MEMBER_KICK
    21,  # MEMBER_PRUNE
    22,  # MEMBER_BAN_ADD
    23,  # MEMBER_BAN_REMOVE
    24,  # MEMBER_UPDATE
    25,  # MEMBER_ROLE_UPDATE
    26,  # MEMBER_MOVE
    27,  # MEMBER_DISCONNECT
    28,  # BOT_ADD
    30,  # ROLE_CREATE
    31,  # ROLE_UPDATE
    32,  # ROLE_DELETE
    33,  # ROLE_POSITION_UPDATE
    40,  # INVITE_CREATE
    41,  # INVITE_UPDATE
    42,  # INVITE_DELETE
    50,  # WEBHOOK_CREATE
    51,  # WEBHOOK_UPDATE
    52,  # WEBHOOK_DELETE
    60,  # EMOJI_CREATE
    61,  # EMOJI_UPDATE
    62,  # EMOJI_DELETE
    72,  # MESSAGE_DELETE
    73,  # MESSAGE_BULK_DELETE
    74,  # MESSAGE_PIN
    75,  # MESSAGE_UNPIN
    80,  # INTEGRATION_CREATE
    81,  # INTEGRATION_UPDATE
    82,  # INTEGRATION_DELETE
    83,  # STAGE_INSTANCE_CREATE
    84,  # STAGE_INSTANCE_UPDATE
    85,  # STAGE_INSTANCE_DELETE
    90,  # STICKER_CREATE
    91,  # STICKER_UPDATE
    92,  # STICKER_DELETE
    100,  # GUILD_SCHEDULED_EVENT_CREATE
    101,  # GUILD_SCHEDULED_EVENT_UPDATE
    102,  # GUILD_SCHEDULED_EVENT_DELETE
    110,  # THREAD_CREATE
    111,  # THREAD_UPDATE
    112,  # THREAD_DELETE
    121,  # APPLICATION_COMMAND_PERMISSION_UPDATE
    130,  # SOUNDBOARD_SOUND_CREATE
    131,  # SOUNDBOARD_SOUND_UPDATE
    132,  # SOUNDBOARD_SOUND_DELETE
    140,  # AUTO_MODERATION_RULE_CREATE
    141,  # AUTO_MODERATION_RULE_UPDATE
    142,  # AUTO_MODERATION_RULE_DELETE
    143,  # AUTO_MODERATION_BLOCK_MESSAGE
    144,  # AUTO_MODERATION_FLAG_TO_CHANNEL
    145,  # AUTO_MODERATION_USER_COMMUNICATION_DISABLED
    146,  # AUTO_MODERATION_QUARANTINE_USER
    150,  # CREATOR_MONETIZATION_REQUEST_CREATED
    151,  # CREATOR_MONETIZATION_REQUEST_ACCEPTED
    163,  # ONBOARDING_PROMPT_CREATE
    164,  # ONBOARDING_PROMPT_UPDATE
    165,  # ONBOARDING_PROMPT_DELETE
    166,  # ONBOARDING_CREATE
    167,  # ONBOARDING_UPDATE
    190,  # HOME_SETTINGS_CREATE
    191,  # HOME_SETTINGS_UPDATE
    192,  # VOICE_CHANNEL_STATUS_CREATE
    193,  # VOICE_CHANNEL_STATUS_DELETE
]


class _AuditLogChangeStr(TypedDict):
    new_value: NotRequired[str]
    old_value: NotRequired[str]
    key: Literal[
        "name",
        "description",
        "preferred_locale",
        "vanity_url_code",
        "topic",
        "code",
        "allow",
        "deny",
        "permissions",
        "tags",
        "status",
    ]


class _AuditLogChangeAssetHash(TypedDict):
    new_value: NotRequired[str]
    old_value: NotRequired[str]
    key: Literal[
        "icon_hash",
        "splash_hash",
        "discovery_splash_hash",
        "banner_hash",
        "avatar_hash",
        "asset",
    ]


class _AuditLogChangeSnowflake(TypedDict):
    new_value: NotRequired[Snowflake]
    old_value: NotRequired[Snowflake]
    key: Literal[
        "id",
        "owner_id",
        "afk_channel_id",
        "rules_channel_id",
        "public_updates_channel_id",
        "widget_channel_id",
        "system_channel_id",
        "application_id",
        "channel_id",
        "inviter_id",
        "guild_id",
    ]


class _AuditLogChangeBool(TypedDict):
    new_value: NotRequired[bool]
    old_value: NotRequired[bool]
    key: Literal[
        "widget_enabled",
        "nsfw",
        "hoist",
        "mentionable",
        "temporary",
        "deaf",
        "mute",
        "nick",
        "enabled_emoticons",
        "rtc_region",
        "available",
        "archived",
        "locked",
    ]


class _AuditLogChangeInt(TypedDict):
    new_value: NotRequired[int]
    old_value: NotRequired[int]
    key: Literal[
        "afk_timeout",
        "prune_delete_days",
        "position",
        "bitrate",
        "rate_limit_per_user",
        "color",
        "max_uses",
        "max_age",
        "user_limit",
        "auto_archive_duration",
        "default_auto_archive_duration",
    ]


class _AuditLogChangeListRole(TypedDict):
    new_value: NotRequired[list[Role]]
    old_value: NotRequired[list[Role]]
    key: Literal["$add", "$remove"]


class _AuditLogChangeMFALevel(TypedDict):
    new_value: NotRequired[MFALevel]
    old_value: NotRequired[MFALevel]
    key: Literal["mfa_level"]


class _AuditLogChangeVerificationLevel(TypedDict):
    new_value: NotRequired[VerificationLevel]
    old_value: NotRequired[VerificationLevel]
    key: Literal["verification_level"]


class _AuditLogChangeExplicitContentFilter(TypedDict):
    new_value: NotRequired[ExplicitContentFilterLevel]
    old_value: NotRequired[ExplicitContentFilterLevel]
    key: Literal["explicit_content_filter"]


class _AuditLogChangeDefaultMessageNotificationLevel(TypedDict):
    new_value: NotRequired[DefaultMessageNotificationLevel]
    old_value: NotRequired[DefaultMessageNotificationLevel]
    key: Literal["default_message_notifications"]


class _AuditLogChangeChannelType(TypedDict):
    new_value: NotRequired[ChannelType]
    old_value: NotRequired[ChannelType]
    key: Literal["type"]


class _AuditLogChangeIntegrationExpireBehaviour(TypedDict):
    new_value: NotRequired[IntegrationExpireBehavior]
    old_value: NotRequired[IntegrationExpireBehavior]
    key: Literal["expire_behavior"]


class _AuditLogChangeVideoQualityMode(TypedDict):
    new_value: NotRequired[VideoQualityMode]
    old_value: NotRequired[VideoQualityMode]
    key: Literal["video_quality_mode"]


class _AuditLogChangeOverwrites(TypedDict):
    new_value: NotRequired[list[PermissionOverwrite]]
    old_value: NotRequired[list[PermissionOverwrite]]
    key: Literal["permission_overwrites"]


AuditLogChange = (
    _AuditLogChangeStr
    | _AuditLogChangeAssetHash
    | _AuditLogChangeSnowflake
    | _AuditLogChangeInt
    | _AuditLogChangeBool
    | _AuditLogChangeListRole
    | _AuditLogChangeMFALevel
    | _AuditLogChangeVerificationLevel
    | _AuditLogChangeExplicitContentFilter
    | _AuditLogChangeDefaultMessageNotificationLevel
    | _AuditLogChangeChannelType
    | _AuditLogChangeIntegrationExpireBehaviour
    | _AuditLogChangeVideoQualityMode
    | _AuditLogChangeOverwrites
)


class AuditEntryInfo(TypedDict):
    application_id: Snowflake
    auto_moderation_rule_name: str
    auto_moderation_rule_trigger_type: str
    channel_id: Snowflake
    count: str
    delete_member_days: str
    id: Snowflake
    members_removed: str
    message_id: Snowflake
    role_name: str
    type: Literal["0", "1"]
    integration_type: str
    status: str


class AuditLogEntry(TypedDict):
    target_id: str | None
    changes: NotRequired[list[AuditLogChange]]
    user_id: Snowflake | None
    id: Snowflake
    action_type: AuditLogEvent
    options: NotRequired[AuditEntryInfo]
    reason: NotRequired[str]


class AuditLog(TypedDict):
    application_commands: list[ApplicationCommand]
    audit_log_entries: list[AuditLogEntry]
    auto_moderation_rules: list[AutoModRule]
    guild_scheduled_events: list[ScheduledEvent]
    integrations: list[PartialIntegration]
    threads: list[Thread]
    users: list[User]
    webhooks: list[Webhook]
