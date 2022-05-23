"""
The MIT License (MIT)

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

import datetime
from typing import TYPE_CHECKING, Optional, List

from . import utils
from .enums import (
    AutoModTriggerType,
    AutoModEventType,
    AutoModActionType,
    try_enum,
)
from .errors import ValidationError
from .mixins import Hashable
from .object import Object

__all__ = (
    "AutoModRule",
)

if TYPE_CHECKING:
    from .abc import Snowflake
    from .guild import Guild
    from .member import Member
    from .state import ConnectionState
    from .types.automod import AutoModRule as AutoModRulePayload
    from .types.automod import AutoModAction as AutoModActionPayload

MISSING = utils.MISSING


class AutoModAction:
    """Represents an action for a guild's auto moderation rule.
    
    .. versionadded:: 2.0
    """

    __slots__ = (
        "type",
        "metadata",
    )

    def __init__(self, data: AutoModActionPayload):
        self.type: AutoModActionType = try_enum(AutoModActionType, data["type"])
        # TODO: Metadata

    def __repr__(self) -> str:
        return f"<AutoModAction type={self.type}>"



class AutoModRule(Hashable):
    """Represents a guild's auto moderation rule.

    .. versionadded:: 2.0
    """

    __slots__ = (
        "_state",
        "id",
        "guild",
        "guild_id",
        "name",
        "creator",
        "creator_id",
        "event_type",
        "trigger_type",
        "actions",
        "enabled",
        "exempt_role_ids",
        "exempt_channel_ids",
    )

    def __init__(
        self,
        *,
        state: ConnectionState,
        guild: Guild,
        creator: Member,
        data: AutoModRulePayload,
    ):
        self._state: ConnectionState = state
        self.id: Snowflake = int(data["id"])
        self.guild: Optional[Guild] = guild
        self.guild_id: Snowflake = int(data["guild_id"])
        self.name: str = data["name"]
        self.creator: Optional[Member] = creator
        self.creator_id: Snowflake = int(data["creator_id"])
        self.event_type: AutoModEventType = try_enum(AutoModEventType, data["event_type"])
        self.trigger_type: AutoModTriggerType = try_enum(AutoModTriggerType, data["trigger_type"])
        # TODO: trigger_metadata
        self.actions: List[AutoModAction] = [AutoModAction(d) for d in data["actions"]]
        self.enabled: bool = data["enabled"]
        self.exempt_role_ids: List[Snowflake] = data["exempt_roles"]
        self.exempt_channel_ids: List[Snowflake] = data["exempt_channels"]

    def __repr__(self) -> str:
        return f"<AutoModRule name={self.name} id={self.id}>"

    def __str__(self) -> str:
        return self.name
