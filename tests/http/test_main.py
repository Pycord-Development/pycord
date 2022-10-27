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
from discord.ext.testing import get_mock_response

from ..core import client
from .core import channel_id, user_id


async def test_logout(client):
    """Test logging out."""
    with client.makes_request(
        Route("POST", "/auth/logout"),
    ):
        await client.http.logout()


@pytest.mark.parametrize(
    "recipients",
    [random.randrange(2**64) for _ in range(10)],
)
async def test_start_group(client, user_id, recipients):
    """Test starting group."""
    payload = {
        "recipients": recipients,
    }
    with client.makes_request(
        Route("POST", "/users/{user_id}/channels", user_id=user_id),
        json=payload,
    ):
        await client.http.start_group(user_id, recipients)


async def test_leave_group(client, channel_id):
    """Test leaving group."""
    with client.makes_request(
        Route("DELETE", "/channels/{channel_id}", channel_id=channel_id),
    ):
        await client.http.leave_group(channel_id)


async def test_start_private_message(client, user_id):
    """Test starting private message."""
    payload = {
        "recipient_id": user_id,
    }
    with client.makes_request(
        Route("POST", "/users/@me/channels"),
        json=payload,
    ):
        await client.http.start_private_message(user_id)


@pytest.mark.parametrize(
    "with_counts",
    (True, False),
)
async def test_get_guild(client, with_counts):
    get_mock_response("get_guild")
    with client.makes_request(
        Route("GET", "/guilds/{guild_id}", guild_id=1234),
        params={"with_counts": int(with_counts)},
    ):
        await client.http.get_guild(1234, with_counts=with_counts)


# async def test_static_login(client):
#     """Test logging in with a static token."""
#     await client.http.close()  # Test closing the client before it exists
#     with client.makes_request(
#         Route("GET", "/users/@me"),
#     ):
#         await client.http.static_login("token")
#     assert client.http.token == "token"
#
#
# @pytest.mark.order(after="test_static_login")
# async def test_close(client):
#     """Test closing the client."""
#     await client.close()
