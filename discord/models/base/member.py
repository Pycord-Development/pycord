from __future__ import annotations

from datetime import datetime
from enum import IntEnum

from pydantic import BaseModel

from ..types import MISSING, AvatarDecorationData, MissingSentinel, RoleID
from ..types.flags import MemberFlags, Permissions
from .user import User


class PremiumType(IntEnum):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2
    NITRO_BASIC = 3


class Member(BaseModel):
    user: User | MissingSentinel = MISSING
    nick: str | None | MissingSentinel = MISSING
    avatar: str | None | MissingSentinel = MISSING
    banner: str | None | MissingSentinel = MISSING
    roles: list[RoleID]
    joined_at: datetime
    premium_since: datetime | None | MissingSentinel = MISSING
    deaf: bool
    mute: bool
    flags: MemberFlags
    pending: bool | MissingSentinel = MISSING
    permissions: Permissions | MissingSentinel = MISSING
    communication_disabled_until: datetime | None | MissingSentinel = MISSING
    avatar_decoration_data: AvatarDecorationData | None | MissingSentinel = MISSING
