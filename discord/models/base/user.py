from __future__ import annotations

from enum import IntEnum

from pydantic import BaseModel

from ..types import (
    MISSING,
    AvatarDecorationData,
    Color,
    Locale,
    MissingSentinel,
    UserID,
)
from ..types.flags import UserFlags


class PremiumType(IntEnum):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2
    NITRO_BASIC = 3


class User(BaseModel):
    id: UserID
    username: str
    discriminator: str
    global_name: str | None
    avatar: str | None
    bot: bool | MissingSentinel = MISSING
    system: bool | MissingSentinel = MISSING
    mfa_enabled: bool | MissingSentinel = MISSING
    banner: str | None | MissingSentinel = MISSING
    accent_color: Color | None | MissingSentinel = MISSING
    locale: Locale | MissingSentinel = MISSING
    verified: bool | MissingSentinel = MISSING
    email: str | MissingSentinel | None = MISSING
    flags: UserFlags | MissingSentinel = MISSING
    premium_type: PremiumType | MissingSentinel = MISSING
    public_flags: UserFlags | MissingSentinel = MISSING
    avatar_decoration_data: AvatarDecorationData | None | MissingSentinel = MISSING
