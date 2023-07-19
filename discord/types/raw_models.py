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

from .._typed_dict import NotRequired, TypedDict
from .automod import AutoModAction, AutoModTriggerType
from .emoji import PartialEmoji
from .member import Member
from .snowflake import Snowflake
from .threads import Thread, ThreadMember
from .user import User


class _MessageEventOptional(TypedDict, total=False):
    guild_id: Snowflake


class MessageDeleteEvent(_MessageEventOptional):
    id: Snowflake
    channel_id: Snowflake


class BulkMessageDeleteEvent(_MessageEventOptional):
    ids: list[Snowflake]
    channel_id: Snowflake


class MessageUpdateEvent(_MessageEventOptional):
    id: Snowflake
    channel_id: Snowflake


class _ReactionEventOptional(TypedDict, total=False):
    guild_id: Snowflake


class ReactionActionEvent(_ReactionEventOptional):
    member: NotRequired[Member]
    user_id: Snowflake
    channel_id: Snowflake
    message_id: Snowflake
    emoji: PartialEmoji


class ReactionClearEvent(_ReactionEventOptional):
    channel_id: Snowflake
    message_id: Snowflake


class ReactionClearEmojiEvent(_ReactionEventOptional):
    channel_id: int
    message_id: int
    emoji: PartialEmoji


class IntegrationDeleteEvent(TypedDict):
    application_id: NotRequired[Snowflake]
    id: Snowflake
    guild_id: Snowflake


ThreadUpdateEvent = Thread


class ThreadDeleteEvent(TypedDict, total=False):
    thread_id: Snowflake
    thread_type: int
    guild_id: Snowflake
    parent_id: Snowflake


class TypingEvent(TypedDict):
    guild_id: NotRequired[Snowflake]
    member: NotRequired[Member]
    channel_id: Snowflake
    user_id: Snowflake
    timestamp: int


class ScheduledEventSubscription(TypedDict, total=False):
    event_id: Snowflake
    user_id: Snowflake
    guild_id: Snowflake


class AutoModActionExecutionEvent(TypedDict):
    channel_id: NotRequired[Snowflake]
    message_id: NotRequired[Snowflake]
    alert_system_message_id: NotRequired[Snowflake]
    matched_keyword: NotRequired[str]
    matched_content: NotRequired[str]
    guild_id: Snowflake
    action: AutoModAction
    rule_id: Snowflake
    rule_trigger_type: AutoModTriggerType
    user_id: Snowflake
    content: str


class MemberRemoveEvent(TypedDict):
    guild_id: Snowflake
    user: User


class ThreadMembersUpdateEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    member_count: int
    added_members: NotRequired[list[ThreadMember]]
    removed_member_ids: NotRequired[list[Snowflake]]
