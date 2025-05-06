from __future__ import annotations

from enum import IntEnum
from typing import Any

from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from ..types import (
    MISSING,
    ChannelID,
    EmojiID,
    GuildID,
    Locale,
    MissingSentinel,
    Permissions,
    SystemChannelFlags,
    UserID,
)
from .emoji import Emoji
from .role import Role
from .sticker import Sticker


class VerificationLevel(IntEnum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


class DefaultNotificationLevel(IntEnum):
    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1


class ExplicitContentFilterLevel(IntEnum):
    DISABLED = 0
    MEMBERS_WITHOUT_ROLES = 1
    ALL_MEMBERS = 2


class GuildFeatures(set[str]):
    def __getattr__(self, item: str) -> bool:
        return item.lower() in self or item in self

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,  # pyright: ignore [reportExplicitAny]
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        def validate_and_create(
            v: Any,
        ) -> GuildFeatures:  # pyright: ignore [reportExplicitAny]
            if isinstance(v, cls):
                return v
            if isinstance(v, (list, set)):
                return cls(
                    str(item) for item in v
                )  # pyright: ignore [reportUnknownArgumentType, reportUnknownVariableType]
            raise ValueError("Invalid input type for GuildFeatures")

        return core_schema.json_or_python_schema(
            # For Python inputs:
            python_schema=core_schema.union_schema(
                [
                    # Accept existing instances
                    core_schema.is_instance_schema(cls),
                    # Accept lists or sets
                    core_schema.no_info_plain_validator_function(validate_and_create),
                ]
            ),
            # For JSON inputs, expecting an array of strings:
            json_schema=core_schema.list_schema(
                core_schema.str_schema(),
                serialization=core_schema.plain_serializer_function_ser_schema(
                    lambda x: list(x),
                    return_schema=core_schema.list_schema(core_schema.str_schema()),
                ),
            ),
            # When serializing to JSON, convert to list
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: list(x),
                return_schema=core_schema.list_schema(core_schema.str_schema()),
                when_used="json",
            ),
        )


class MFALevel(IntEnum):
    NONE = 0
    ELEVATED = 1


class PremiumTier(IntEnum):
    NONE = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class NSFWLevel(IntEnum):
    DEFAULT = 0
    EXPLICIT = 1
    SAFE = 2
    AGE_RESTRICTED = 3


class BaseGuild(BaseModel):
    id: GuildID


class UnavailableGuild(BaseGuild):
    unavailable: bool = True


class Guild(BaseGuild):
    name: str = Field(min_length=2, max_length=100)
    icon: str | MissingSentinel | None = Field(alias="icon_hash", default=MISSING)
    splash: str | None
    discovery_splash: str | None
    owner: bool | MissingSentinel = Field(default=MISSING)
    owner_id: UserID
    permissions: Permissions | MissingSentinel = Field(default=MISSING)
    afk_channel_id: ChannelID | None
    afk_timeout: int
    widget_enabled: bool | MissingSentinel = Field(default=MISSING)
    widget_channel_id: ChannelID | None | MissingSentinel = Field(default=MISSING)
    verification_level: VerificationLevel
    default_message_notifications: DefaultNotificationLevel
    explicit_content_filter: ExplicitContentFilterLevel
    roles: list[Role]
    emojis: list[Emoji]
    features: GuildFeatures
    mfa_level: MFALevel
    application_id: UserID | None
    system_channel_id: ChannelID | None
    system_channel_flags: SystemChannelFlags
    rules_channel_id: ChannelID | None
    max_presences: int | None | MissingSentinel = Field(default=MISSING)
    max_members: int | MissingSentinel = Field(default=MISSING)
    vanity_url_code: str | None
    description: str | None
    banner: str | None
    premium_tier: PremiumTier
    premium_subscription_count: int | None
    preferred_locale: Locale
    public_updates_channel_id: ChannelID | None
    max_video_channel_users: int | MissingSentinel = Field(default=MISSING)
    max_stage_video_channel_users: int | MissingSentinel = Field(default=MISSING)
    approximate_member_count: int | MissingSentinel = Field(default=MISSING)
    approximate_presence_count: int | MissingSentinel = Field(default=MISSING)
    welcome_screen: WelcomeScreen | None
    nsfw_level: NSFWLevel
    stickers: list[Sticker] | MissingSentinel = Field(default=MISSING)
    premium_progress_bar_enabled: bool
    safety_alerts_channel_id: ChannelID | None


class WelcomeScreen(BaseModel):
    description: str | None
    welcome_channels: list[WelcomeScreenChannel]


class WelcomeScreenChannel(BaseModel):
    channel_id: ChannelID
    description: str
    emoji_id: EmojiID | None
    emoji_name: str | None
