from __future__ import annotations

from pydantic import BaseModel

from ..types import MISSING, EmojiID, MissingSentinel, RoleID
from .user import User


class Emoji(BaseModel):
    id: EmojiID | None
    name: str
    roles: list[RoleID] | MissingSentinel = MISSING
    user: User | MissingSentinel = MISSING
    require_colons: bool | MissingSentinel = MISSING
    managed: bool | MissingSentinel = MISSING
    animated: bool | MissingSentinel = MISSING
    available: bool | MissingSentinel = MISSING
