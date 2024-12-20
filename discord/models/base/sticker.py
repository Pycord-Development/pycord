from __future__ import annotations

from enum import IntEnum

from pydantic import BaseModel

from ..types import MISSING, GuildID, MissingSentinel, Snowflake, StickerID
from .user import User


class StickerType(IntEnum):
    STANDARD = 1
    GUILD = 2


class StickerFormatType(IntEnum):
    PNG = 1
    APNG = 1
    LOTTIE = 3
    GIF = 4


class Sticker(BaseModel):
    id: StickerID | None
    pack_id: Snowflake | MissingSentinel = MISSING
    name: str
    description: str | None
    tags: str
    type: StickerType
    format_type: StickerFormatType
    available: bool | MissingSentinel = MISSING
    guild_id: GuildID | MissingSentinel = MISSING
    user: User | MissingSentinel = MISSING
    sort_value: int | MissingSentinel = MISSING


class StickerPack(BaseModel):
    id: Snowflake
    stickers: list[Sticker]
    name: str
    sku_id: Snowflake
    cover_sticker_id: StickerID | MissingSentinel = MISSING
    description: str
    banner_asset_id: Snowflake | MissingSentinel = MISSING
