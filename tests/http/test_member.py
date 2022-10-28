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

import pytest

from discord import Route

from ..core import client
from .core import guild_id, reason, user_id


async def test_kick(client, guild_id, user_id, reason):
    """Test kicking a member."""
    with client.makes_request(
        Route(
            "DELETE",
            "/guilds/{guild_id}/members/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        ),
        reason=reason,
    ):
        await client.http.kick(user_id, guild_id, reason=reason)


@pytest.mark.parametrize(
    "delete_message_days",
    (None, random.randint(0, 7)),
)
@pytest.mark.parametrize("delete_message_seconds", (None, random.randint(0, 604800)))
async def test_ban(
    client,
    guild_id,
    user_id,
    delete_message_seconds,
    delete_message_days,
    reason,
):
    """Test banning a member."""
    route = Route(
        "PUT",
        "/guilds/{guild_id}/bans/{user_id}",
        guild_id=guild_id,
        user_id=user_id,
    )
    args = (user_id, guild_id, delete_message_seconds, delete_message_days, reason)
    params = {}
    if delete_message_seconds:
        params = {"delete_message_seconds": delete_message_seconds}
    if delete_message_days and not delete_message_seconds:
        params = params or {"delete_message_days": delete_message_days}
        with client.makes_request(
            route,
            params=params,
            reason=reason,
        ):
            with pytest.warns(DeprecationWarning):
                await client.http.ban(*args)
    else:
        with client.makes_request(
            route,
            params=params,
            reason=reason,
        ):
            await client.http.ban(*args)


async def test_unban(client, guild_id, user_id, reason):
    """Test unbanning a member."""
    with client.makes_request(
        Route(
            "DELETE",
            "/guilds/{guild_id}/bans/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        ),
        reason=reason,
    ):
        await client.http.unban(user_id, guild_id, reason=reason)
