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

import random
from typing import get_args

import pytest

from discord import Route
from discord.ext.testing.fixtures import (
    allowed_mentions,
    applied_tags,
    before,
    channel_id,
    components,
    content,
)
from discord.ext.testing.fixtures import embed as embed_
from discord.ext.testing.fixtures import (
    embeds,
    guild_id,
    invitable,
    limit,
    message_id,
    name,
    nonce,
    reason,
    stickers,
    user_id,
)
from discord.ext.testing.helpers import random_archive_duration
from discord.types import channel, threads

from ..core import client


@pytest.fixture
def auto_archive_duration() -> threads.ThreadArchiveDuration:
    return random_archive_duration()


@pytest.fixture(params=(random.choice(get_args(channel.ChannelType)),))
def type_(request) -> channel.ChannelType:
    return request.param


@pytest.fixture(params=(random.randint(0, 21600), None))
def rate_limit_per_user(request) -> int | None:
    return request.param


async def test_start_thread_with_message(
    client, channel_id, message_id, name, auto_archive_duration, reason
):
    payload = {
        "name": name,
        "auto_archive_duration": auto_archive_duration,
    }
    with client.makes_request(
        Route(
            "POST",
            "/channels/{channel_id}/messages/{message_id}/threads",
            channel_id=channel_id,
            message_id=message_id,
        ),
        json=payload,
        reason=reason,
    ):
        await client.http.start_thread_with_message(
            channel_id,
            message_id,
            name=name,
            auto_archive_duration=auto_archive_duration,
            reason=reason,
        )


async def test_start_thread_without_message(
    client, channel_id, name, auto_archive_duration, type_, invitable, reason
):
    payload = {
        "name": name,
        "auto_archive_duration": auto_archive_duration,
        "type": type_,
        "invitable": invitable,
    }
    with client.makes_request(
        Route(
            "POST",
            "/channels/{channel_id}/threads",
            channel_id=channel_id,
        ),
        json=payload,
        reason=reason,
    ):
        await client.http.start_thread_without_message(
            channel_id,
            name=name,
            auto_archive_duration=auto_archive_duration,
            type=type_,
            invitable=invitable,
            reason=reason,
        )


async def test_start_forum_thread(
    client,
    channel_id,
    content,
    name,
    auto_archive_duration,
    rate_limit_per_user,
    invitable,
    applied_tags,
    reason,
    embed,
    embeds,
    nonce,
    allowed_mentions,
    stickers,
    components,
):
    payload = {
        "name": name,
        "auto_archive_duration": auto_archive_duration,
        "invitable": invitable,
    }
    if content:
        payload["content"] = content
    if applied_tags:
        payload["applied_tags"] = applied_tags
    if embed:
        payload["embeds"] = [embed]
    if embeds:
        payload["embeds"] = embeds
    if nonce:
        payload["nonce"] = nonce
    if allowed_mentions:
        payload["allowed_mentions"] = allowed_mentions
    if components:
        payload["components"] = components
    if stickers:
        payload["sticker_ids"] = stickers
    if rate_limit_per_user:
        payload["rate_limit_per_user"] = rate_limit_per_user
    with client.makes_request(
        Route(
            "POST",
            "/channels/{channel_id}/threads?has_message=true",
            channel_id=channel_id,
        ),
        json=payload,
        reason=reason,
    ):
        await client.http.start_forum_thread(
            channel_id,
            content=content,
            name=name,
            auto_archive_duration=auto_archive_duration,
            rate_limit_per_user=rate_limit_per_user,
            invitable=invitable,
            applied_tags=applied_tags,
            reason=reason,
            embed=embed,
            embeds=embeds,
            nonce=nonce,
            allowed_mentions=allowed_mentions,
            stickers=stickers,
            components=components,
        )


async def test_join_thread(client, channel_id):
    with client.makes_request(
        Route(
            "PUT", "/channels/{channel_id}/thread-members/@me", channel_id=channel_id
        ),
    ):
        await client.http.join_thread(channel_id)


async def test_add_user_to_thread(client, channel_id, user_id):
    with client.makes_request(
        Route(
            "PUT",
            "/channels/{channel_id}/thread-members/{user_id}",
            channel_id=channel_id,
            user_id=user_id,
        ),
    ):
        await client.http.add_user_to_thread(channel_id, user_id)


async def test_leave_thread(client, channel_id):
    with client.makes_request(
        Route(
            "DELETE", "/channels/{channel_id}/thread-members/@me", channel_id=channel_id
        ),
    ):
        await client.http.leave_thread(channel_id)


async def test_remove_user_from_thread(client, channel_id, user_id):
    with client.makes_request(
        Route(
            "DELETE",
            "/channels/{channel_id}/thread-members/{user_id}",
            channel_id=channel_id,
            user_id=user_id,
        ),
    ):
        await client.http.remove_user_from_thread(channel_id, user_id)


async def test_get_public_archived_threads(client, channel_id, before, limit):
    params = {"limit": limit}
    if before:
        params["before"] = before
    with client.makes_request(
        Route(
            "GET",
            "/channels/{channel_id}/threads/archived/public",
            channel_id=channel_id,
        ),
        params=params,
    ):
        await client.http.get_public_archived_threads(channel_id, before, limit)


async def test_get_private_archived_threads(client, channel_id, before, limit):
    params = {"limit": limit}
    if before:
        params["before"] = before
    with client.makes_request(
        Route(
            "GET",
            "/channels/{channel_id}/threads/archived/private",
            channel_id=channel_id,
        ),
        params=params,
    ):
        await client.http.get_private_archived_threads(channel_id, before, limit)


async def test_get_joined_private_archived_threads(client, channel_id, before, limit):
    params = {"limit": limit}
    if before:
        params["before"] = before
    with client.makes_request(
        Route(
            "GET",
            "/channels/{channel_id}/users/@me/threads/archived/private",
            channel_id=channel_id,
        ),
        params=params,
    ):
        await client.http.get_joined_private_archived_threads(channel_id, before, limit)


async def test_get_active_threads(client, guild_id):
    with client.makes_request(
        Route("GET", "/guilds/{guild_id}/threads/active", guild_id=guild_id),
    ):
        await client.http.get_active_threads(guild_id)


async def test_get_thread_members(client, channel_id):
    with client.makes_request(
        Route("GET", "/channels/{channel_id}/thread-members", channel_id=channel_id),
    ):
        await client.http.get_thread_members(channel_id)
