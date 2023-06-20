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
import pytest

from discord import Route
from discord.ext.testing.fixtures import avatar, channel_id, guild_id, name, reason
from discord.ext.testing.helpers import random_snowflake

from ..core import client


@pytest.fixture
def webhook_id() -> int:
    return random_snowflake()


@pytest.fixture
def webhook_channel_id() -> int:
    return random_snowflake()


async def test_create_webhook(client, channel_id, name, avatar, reason):
    payload = {"name": name}
    if avatar is not None:
        payload["avatar"] = avatar
    with client.makes_request(
        Route("POST", "/channels/{channel_id}/webhooks", channel_id=channel_id),
        json=payload,
        reason=reason,
    ):
        await client.http.create_webhook(
            channel_id, name=name, avatar=avatar, reason=reason
        )


async def test_channel_webhooks(client, channel_id):
    with client.makes_request(
        Route("GET", "/channels/{channel_id}/webhooks", channel_id=channel_id),
    ):
        await client.http.channel_webhooks(channel_id)


async def test_guild_webhooks(client, guild_id):
    with client.makes_request(
        Route("GET", "/guilds/{guild_id}/webhooks", guild_id=guild_id),
    ):
        await client.http.guild_webhooks(guild_id)


async def test_get_webhook(client, webhook_id):
    with client.makes_request(
        Route("GET", "/webhooks/{webhook_id}", webhook_id=webhook_id)
    ):
        await client.http.get_webhook(webhook_id)


async def test_follow_webhook(client, channel_id, webhook_channel_id, reason):
    payload = {"webhook_channel_id": str(webhook_channel_id)}
    with client.makes_request(
        Route("POST", "/channels/{channel_id}/followers", channel_id=channel_id),
        json=payload,
        reason=reason,
    ):
        await client.http.follow_webhook(channel_id, webhook_channel_id, reason)
