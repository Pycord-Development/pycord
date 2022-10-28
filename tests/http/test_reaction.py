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

from discord import Route

from ..core import client
from .core import after, channel_id, emoji, limit, message_id, user_id


async def test_add_reaction(client, channel_id, message_id, emoji):
    """Test adding reaction."""
    with client.makes_request(
        Route(
            "PUT",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji,
        ),
    ):
        await client.http.add_reaction(channel_id, message_id, emoji)


async def test_remove_reaction(client, channel_id, message_id, user_id, emoji):
    """Test removing reaction."""
    with client.makes_request(
        Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{member_id}",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji,
            member_id=user_id,
        ),
    ):
        await client.http.remove_reaction(channel_id, message_id, emoji, user_id)


async def test_remove_own_reaction(client, channel_id, message_id, emoji):
    """Test removing own reaction."""
    with client.makes_request(
        Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji,
        ),
    ):
        await client.http.remove_own_reaction(channel_id, message_id, emoji)


async def test_get_reaction_users(client, channel_id, message_id, limit, after, emoji):
    """Test getting reaction users."""
    params = {"limit": limit}
    if after is not None:
        params["after"] = after
    with client.makes_request(
        Route(
            "GET",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji,
        ),
        params=params,
    ):
        await client.http.get_reaction_users(
            channel_id, message_id, emoji, limit, after
        )


async def test_clear_reactions(client, channel_id, message_id):
    """Test clearing reactions."""
    with client.makes_request(
        Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions",
            channel_id=channel_id,
            message_id=message_id,
        ),
    ):
        await client.http.clear_reactions(channel_id, message_id)


async def test_clear_single_reaction(client, channel_id, message_id, emoji):
    """Test clearing single reaction."""
    with client.makes_request(
        Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji,
        ),
    ):
        await client.http.clear_single_reaction(channel_id, message_id, emoji)
