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

from ..core import client
from .core import after, before, guild_id, icon, limit, name


async def test_get_guilds(client, limit, before, after):
    params = {"limit": limit}
    if before:
        params["before"] = before
    if after:
        params["after"] = after
    with client.makes_request(Route("GET", "/users/@me/guilds"), params=params):
        await client.http.get_guilds(limit, before, after)


async def test_leave_guild(client, guild_id):
    with client.makes_request(
        Route("DELETE", "/users/@me/guilds/{guild_id}", guild_id=guild_id)
    ):
        await client.http.leave_guild(guild_id)


@pytest.mark.parametrize(
    "with_counts",
    (True, False),
)
async def test_get_guild(client, guild_id, with_counts):
    with client.makes_request(
        Route("GET", "/guilds/{guild_id}", guild_id=guild_id),
        params={"with_counts": int(with_counts)},
    ):
        await client.http.get_guild(guild_id, with_counts=with_counts)


async def test_delete_guild(client, guild_id):
    with client.makes_request(Route("DELETE", "/guilds/{guild_id}", guild_id=guild_id)):
        await client.http.delete_guild(guild_id)


async def test_create_guild(client, name, icon):
    payload = {"name": name}
    if icon:
        payload["icon"] = icon
    with client.makes_request(Route("POST", "/guilds"), json=payload):
        await client.http.create_guild(name, icon)
