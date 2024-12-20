from __future__ import annotations

from pydantic import BaseModel, field_validator

from ..guild import Guild, UnavailableGuild
from ..types.utils import MISSING, MissingSentinel
from ..user import User
from .base import GatewayEvent


class ReadyData(BaseModel):
    v: int
    user: User
    private_channels: list[dict]  # TODO: Channel
    guilds: list[Guild | UnavailableGuild]
    session_id: str
    shard: list[int] | MissingSentinel = MISSING
    application: dict  # TODO: Application

    # @field_validator("guilds", mode='plain')
    # def guilds_validator(cls, guilds: list[dict[str, Any]]) -> list[Guild | UnavailableGuild]:  # pyright: ignore [reportExplicitAny]
    #    r: list[Guild | UnavailableGuild] = []
    #    for guild in guilds:
    #        if guild.get("unavailable", False):
    #            r.append(UnavailableGuild(**guild))
    #        else:
    #            r.append(Guild(**guild))
    #    return r


class Ready(GatewayEvent[ReadyData]):
    pass
