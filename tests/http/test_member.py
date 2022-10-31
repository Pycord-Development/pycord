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
from typing import Any

import pytest

from discord import Route

from ..core import client
from .core import guild_id, random_dict, reason, user_id


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


@pytest.mark.parametrize(
    "mute",
    (None, True, False),
)
@pytest.mark.parametrize(
    "deafen",
    (None, True, False),
)
async def test_guild_voice_state(client, user_id, guild_id, mute, deafen, reason):
    """Test modifying a member's voice state."""
    payload = {}
    if mute is not None:
        payload["mute"] = mute
    if deafen is not None:
        payload["deaf"] = deafen
    with client.makes_request(
        Route(
            "PATCH",
            "/guilds/{guild_id}/members/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        ),
        json=payload,
        reason=reason,
    ):
        await client.http.guild_voice_state(
            user_id, guild_id, mute=mute, deafen=deafen, reason=reason
        )


@pytest.mark.parametrize("payload", [random_dict()])
async def test_edit_profile(client, guild_id, payload):
    """Test editing the current user profile."""
    with client.makes_request(Route("PATCH", "/users/@me"), json=payload):
        await client.http.edit_profile(payload)


@pytest.mark.parametrize(
    "nickname",
    ("test",),  # TODO: Randomize nickname param
)
async def test_change_my_nickname(
    client, guild_id: int, nickname: str, reason: str | None
):
    with client.makes_request(
        Route(
            "PATCH",
            "/guilds/{guild_id}/members/@me",
            guild_id=guild_id,
        ),
        json={"nick": nickname},
        reason=reason,
    ):
        await client.http.change_my_nickname(guild_id, nickname, reason=reason)


@pytest.mark.parametrize(
    "nickname",
    ("test",),  # TODO: Randomize nickname param
)
async def test_change_nickname(
    client, guild_id: int, user_id: int, nickname: str, reason: str | None
):
    with client.makes_request(
        Route(
            "PATCH",
            "/guilds/{guild_id}/members/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        ),
        json={"nick": nickname},
        reason=reason,
    ):
        await client.http.change_nickname(guild_id, user_id, nickname, reason=reason)


@pytest.mark.parametrize("payload", [random_dict()])
async def test_edit_my_voice_state(client, guild_id: int, payload: dict[str, Any]):
    with client.makes_request(
        Route(
            "PATCH",
            "/guilds/{guild_id}/voice-states/@me",
            guild_id=guild_id,
        ),
        json=payload,
    ):
        await client.http.edit_my_voice_state(guild_id, payload)


@pytest.mark.parametrize("payload", [random_dict()])
async def test_edit_voice_state(
    client, guild_id: int, user_id: int, payload: dict[str, Any]
):
    with client.makes_request(
        Route(
            "PATCH",
            "/guilds/{guild_id}/voice-states/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        ),
        json=payload,
    ):
        await client.http.edit_voice_state(guild_id, user_id, payload)


@pytest.mark.parametrize("payload", [random_dict()])
async def test_edit_member(
    client, guild_id: int, user_id: int, payload: dict[str, Any], reason: str | None
):
    with client.makes_request(
        Route(
            "PATCH",
            "/guilds/{guild_id}/members/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        ),
        json=payload,
        reason=reason,
    ):
        await client.http.edit_member(guild_id, user_id, **payload, reason=reason)
