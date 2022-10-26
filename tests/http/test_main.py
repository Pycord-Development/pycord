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
from discord.ext.testing import get_mock_response

from ..core import client


async def test_logout(client):
    """Test logging out."""
    with client.makes_request(
        Route("POST", "/auth/logout"),
    ):
        await client.http.logout()


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
