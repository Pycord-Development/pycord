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

from typing import Literal

from typing_extensions import NotRequired, TypedDict

from .snowflake import Snowflake

AutoModTriggerType = Literal[
    1,  # KEYWORD
    3,  # SPAM
    4,  # KEYWORD_PRESET
    5,  # MENTION_SPAM
    6,  # MEMBER_PROFILE
]

AutoModEventType = Literal[
    1,  # MESSAGE_SEND
    2,  # MEMBER_UPDATE
]

AutoModActionType = Literal[
    1,  # BLOCK_MESSAGE
    2,  # SEND_ALERT_MESSAGE
    3,  # TIMEOUT
    4,  # BLOCK_MEMBER_INTERACTION
]

AutoModKeywordPresetType = Literal[
    1,  # PROFANITY
    2,  # SEXUAL_CONTENT
    3,  # SLURS
]


class AutoModTriggerMetadata(TypedDict):
    keyword_filter: list[str]
    regex_patterns: list[str]
    presets: list[AutoModKeywordPresetType]
    allow_list: list[str]
    mention_total_limit: int
    mention_raid_protection_enabled: bool


class AutoModActionMetadata(TypedDict):
    channel_id: Snowflake
    duration_seconds: int
    custom_message: NotRequired[str]


class AutoModAction(TypedDict):
    type: AutoModActionType
    metadata: NotRequired[AutoModActionMetadata]


class AutoModRule(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    name: str
    creator_id: Snowflake
    event_type: AutoModEventType
    trigger_type: AutoModTriggerType
    trigger_metadata: AutoModTriggerMetadata
    actions: list[AutoModAction]
    enabled: bool
    exempt_roles: list[Snowflake]
    exempt_channels: list[Snowflake]


class CreateAutoModRule(TypedDict):
    """Payload sent when creating an automod rule"""

    name: str
    event_type: AutoModEventType
    trigger_type: AutoModTriggerType
    trigger_metadata: NotRequired[AutoModTriggerMetadata]
    actions: list[AutoModAction]
    enabled: NotRequired[bool]
    exempt_roles: NotRequired[list[Snowflake]]
    exempt_channels: NotRequired[list[Snowflake]]


class EditAutoModRule(TypedDict):
    """Payload sent when editing an automod rule"""

    name: str
    event_type: AutoModEventType
    trigger_metadata: NotRequired[AutoModTriggerMetadata]
    actions: list[AutoModAction]
    enabled: bool
    exempt_roles: list[Snowflake]
    exempt_channels: list[Snowflake]
