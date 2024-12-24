from __future__ import annotations

from typing import Any

from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    SerializerFunctionWrapHandler,
    model_serializer,
)
from typing_extensions import Annotated

from ..types import (
    MISSING,
    Color,
    MissingSentinel,
    Permissions,
    RoleFlags,
    RoleID,
    Snowflake,
    UserID,
)


def presence_bool(v: Any) -> bool:  # pyright: ignore [reportExplicitAny]
    return True if v is not None else False


PresentBool = Annotated[bool, BeforeValidator(presence_bool)]


class RoleTags(BaseModel):
    bot_id: UserID | MissingSentinel = Field(default=MISSING)
    integration_id: UserID | MissingSentinel = Field(default=MISSING)
    premium_subscriber: PresentBool = False
    subscription_listing_id: Snowflake | MissingSentinel = Field(default=MISSING)
    available_for_purchase: PresentBool = False
    guild_connections: PresentBool = False

    @model_serializer(mode="wrap")
    def serialize_model(
        self, nxt: SerializerFunctionWrapHandler
    ) -> dict[Any, Any]:  # pyright: ignore [reportExplicitAny]
        return {k: v for k, v in nxt(self).items() if v is not False}


class Role(BaseModel):
    id: RoleID
    name: str
    color: Color = Field(alias="colour")
    hoist: bool
    icon: str | None | MissingSentinel = Field(default=MISSING)
    unicode_emoji: str | None | MissingSentinel = Field(default=MISSING)
    position: int
    permissions: Permissions
    managed: bool
    mentionable: bool
    tags: RoleTags | MissingSentinel = Field(default=MISSING)
    flags: RoleFlags
