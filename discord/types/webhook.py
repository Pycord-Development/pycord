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

from typing import Literal

from .._typed_dict import NotRequired, TypedDict
from .channel import PartialChannel
from .snowflake import Snowflake
from .user import User


class SourceGuild(TypedDict):
    id: int
    name: str
    icon: str


WebhookType = Literal[1, 2, 3]


class PartialWebhook(TypedDict):
    guild_id: NotRequired[Snowflake]
    user: NotRequired[User]
    token: NotRequired[str]
    id: Snowflake
    type: WebhookType


class FollowerWebhook(PartialWebhook):
    source_channel: NotRequired[PartialChannel]
    source_guild: NotRequired[SourceGuild]
    channel_id: Snowflake
    webhook_id: Snowflake


class Webhook(PartialWebhook):
    name: NotRequired[str | None]
    avatar: NotRequired[str | None]
    channel_id: NotRequired[Snowflake]
    application_id: NotRequired[Snowflake | None]
