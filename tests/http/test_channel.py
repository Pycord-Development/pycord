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
from discord.ext.testing.fixtures import channel_id, guild_id, invitable, name, reason
from discord.ext.testing.helpers import (
    powerset,
    random_archive_duration,
    random_bool,
    random_count,
    random_overwrite,
    random_snowflake,
)
from discord.types import channel, guild, threads

from ..core import client


@pytest.fixture(params=(random_snowflake(),))
def parent_id(request) -> int:
    return request.param


@pytest.fixture(params=("test topic",))  # TODO: Make channel topic random
def topic(request) -> str:
    return request.param


@pytest.fixture(params=(random.randint(8000, 384000),))
def bitrate(request) -> int:
    return request.param


@pytest.fixture(params=(random_bool(),))
def nsfw(request) -> bool | None:
    return request.param


@pytest.fixture(params=(random.randint(0, 99),))
def user_limit(request) -> int | None:
    return request.param


@pytest.fixture(params=(random.randint(0, 99),))
def position(request) -> int | None:
    """A random position fixture."""
    # Note: This could theoretically go higher than 99
    return request.param


@pytest.fixture(params=(random_count(),))
def permission_overwrites(request) -> list[channel.PermissionOverwrite] | None:
    if request.param is None:
        return None
    return [random_overwrite() for _ in range(request.param)]


@pytest.fixture(params=(random.choice(get_args(channel.ChannelType)),))
def type_(request) -> channel.ChannelType:
    return request.param


@pytest.fixture(params=("test region",))  # TODO: Make channel region random
def rtc_region(request) -> str | None:
    return request.param


@pytest.fixture(params=(random.choice(get_args(channel.VideoQualityMode)),))
def video_quality_mode(request) -> channel.VideoQualityMode:
    return request.param


@pytest.fixture(params=(random_bool(),))
def archived(request) -> bool | None:
    return request.param


@pytest.fixture(params=(random.choice(get_args(threads.ThreadArchiveDuration)),))
def auto_archive_duration(request) -> threads.ThreadArchiveDuration | None:
    return request.param


@pytest.fixture(params=(random_bool(),))
def locked(request) -> bool | None:
    return request.param


@pytest.fixture
def default_auto_archive_duration() -> threads.ThreadArchiveDuration | None:
    return random_archive_duration()


@pytest.fixture(params=(random.randint(0, 21600),))
def rate_limit_per_user(request) -> int | None:
    return request.param


@pytest.fixture(params=powerset(["id", "position", "lock_permissions", "parent_id"]))
def channel_position_updates_payload(
    request, channel_id, position, locked, parent_id
) -> list[guild.ChannelPositionUpdate]:
    return [
        guild.ChannelPositionUpdate(
            id=channel_id if "id" in request.param else None,
            position=position if "position" in request.param else None,
            lock_permissions=locked if "lock_permissions" in request.param else None,
            parent_id=parent_id if "parent_id" in request.param else None,
        )
    ]


@pytest.mark.parametrize(
    "include",
    [
        random.sample(
            [
                "name",
                "parent_id",
                "topic",
                "bitrate",
                "nsfw",
                "user_limit",
                "position",
                "permission_overwrites",
                "rate_limit_per_user",
                "type",
                "rtc_region",
                "video_quality_mode",
                "archived",
                "auto_archive_duration",
                "locked",
                "invitable",
                "default_auto_archive_duration",
            ],
            i,
        )
        for i in range(17)
    ],
)
async def test_edit_channel(
    client,
    channel_id,
    name,
    parent_id,
    topic,
    bitrate,
    nsfw,
    user_limit,
    position,
    permission_overwrites,
    rate_limit_per_user,
    type_,
    rtc_region,
    video_quality_mode,
    archived,
    auto_archive_duration,
    locked,
    invitable,
    default_auto_archive_duration,
    reason,
    include,  # We use this because testing all combinations would result in 200k tests
):
    payload = {
        "name": name,
        "parent_id": parent_id,
        "topic": topic,
        "bitrate": bitrate,
        "nsfw": nsfw,
        "user_limit": user_limit,
        "position": position,
        "permission_overwrites": permission_overwrites,
        "rate_limit_per_user": rate_limit_per_user,
        "type": type_,
        "rtc_region": rtc_region,
        "video_quality_mode": video_quality_mode,
        "archived": archived,
        "auto_archive_duration": auto_archive_duration,
        "locked": locked,
        "invitable": invitable,
        "default_auto_archive_duration": default_auto_archive_duration,
    }
    payload = {k: v for k, v in payload.items() if k in include}
    with client.makes_request(
        Route("PATCH", "/channels/{channel_id}", channel_id=channel_id),
        json=payload,
        reason=reason,
    ):
        await client.http.edit_channel(channel_id, **payload, reason=reason)


async def test_bulk_channel_update(
    client,
    guild_id,
    channel_position_updates_payload,
    reason,
):
    with client.makes_request(
        Route("PATCH", "/guilds/{guild_id}/channels", guild_id=guild_id),
        json=[channel_position_updates_payload],
        reason=reason,
    ):
        await client.http.bulk_channel_update(
            guild_id, [channel_position_updates_payload], reason=reason
        )


@pytest.mark.parametrize(
    "include",
    [
        random.sample(
            (
                "name",
                "parent_id",
                "topic",
                "bitrate",
                "nsfw",
                "user_limit",
                "position",
                "permission_overwrites",
                "rate_limit_per_user",
                "rtc_region",
                "video_quality_mode",
                "auto_archive_duration",
            ),
            i,
        )
        for i in range(12)
    ],
)
async def test_create_channel(
    client,
    guild_id,
    type_,
    name,
    parent_id,
    topic,
    bitrate,
    nsfw,
    user_limit,
    position,
    permission_overwrites,
    rate_limit_per_user,
    rtc_region,
    video_quality_mode,
    auto_archive_duration,
    reason,
    include,
):
    payload = {
        "type": type_,
        "name": name,
        "parent_id": parent_id,
        "topic": topic,
        "bitrate": bitrate,
        "nsfw": nsfw,
        "user_limit": user_limit,
        "position": position,
        "permission_overwrites": permission_overwrites,
        "rate_limit_per_user": rate_limit_per_user,
        "rtc_region": rtc_region,
        "video_quality_mode": video_quality_mode,
        "auto_archive_duration": auto_archive_duration,
    }
    payload = {k: v for k, v in payload.items() if k in include}
    with client.makes_request(
        Route("POST", "/guilds/{guild_id}/channels", guild_id=guild_id),
        json={"type": type_, **payload},
        reason=reason,
    ):
        await client.http.create_channel(guild_id, type_, **payload, reason=reason)


async def test_delete_channel(client, channel_id, reason):
    with client.makes_request(
        Route("DELETE", "/channels/{channel_id}", channel_id=channel_id),
        reason=reason,
    ):
        await client.http.delete_channel(channel_id, reason=reason)
