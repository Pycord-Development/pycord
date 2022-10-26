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
import random
from itertools import chain, combinations
from typing import Iterable, TypeVar

import pytest

from discord import Route
from discord.ext.testing import get_mock_response
from discord.types import embed, message, sticker

from ..core import client

V = TypeVar("V")


def powerset(iterable: Iterable[V]) -> Iterable[Iterable[V]]:
    # https://docs.python.org/3/library/itertools.html#itertools-recipes
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def random_combination(iterable: Iterable[V]) -> Iterable[V]:
    return random.choice(list(powerset(iterable)))


def random_snowflake() -> int:
    """Generate a random snowflake."""
    return random.randint(0, 2**64 - 1)


def random_embed() -> embed.Embed:
    # TODO: Improve this
    return embed.Embed(
        title="Test",
    )


def random_bool() -> bool:
    return random.random() > 0.5


def random_allowed_mentions() -> message.AllowedMentions:
    parse: list[message.AllowedMentionType] = ["roles", "users", "everyone"]
    return message.AllowedMentions(
        parse=list(random_combination(parse)),
        roles=[random_snowflake() for _ in range(5)] if random_bool() else None,
        users=[random_snowflake() for _ in range(5)] if random_bool() else None,
        replied_user=random.random() > 0.5,
    )


def random_message_reference() -> message.MessageReference:
    return message.MessageReference(
        message_id=random_snowflake() if random_bool() else None,
        channel_id=random_snowflake() if random_bool() else None,
        guild_id=random_snowflake() if random_bool() else None,
        fail_if_not_exists=random.random() > 0.5 if random_bool() else None,
    )


def random_sticker() -> sticker.StickerItem:
    return sticker.StickerItem(
        id=random_snowflake(),
        name="test",
        format_type=random.choice([1, 2, 3]),
    )


@pytest.fixture
def user_id() -> int:
    """A random user ID."""
    return random_snowflake()


@pytest.fixture
def channel_id() -> int:
    return random_snowflake()


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


@pytest.mark.parametrize("content", (None, "Hello, World!"))
@pytest.mark.parametrize(
    "tts",
    (True, False),
)
@pytest.mark.parametrize(
    "embed",
    (None, random_embed()),
)
@pytest.mark.parametrize(
    "embeds",
    (None, [random_embed() for _ in range(10)]),
)
@pytest.mark.parametrize(
    "nonce",
    (None, "..."),
)
@pytest.mark.parametrize(
    "allowed_mentions",
    (None, random_allowed_mentions()),
)
@pytest.mark.parametrize(
    "message_reference",
    (None, random_message_reference()),
)
@pytest.mark.parametrize(
    "stickers",
    (None, [random_sticker() for _ in range(10)]),
)
@pytest.mark.parametrize(
    "components",
    (None,),  # TODO: Add this
)
@pytest.mark.parametrize(
    "flags",
    (None,),  # TODO: Add this
)
async def test_send_message(
    client,
    channel_id,
    content,
    tts,
    embed,
    embeds,
    nonce,
    allowed_mentions,
    message_reference,
    stickers,
    components,
    flags,
):
    payload = {
        "content": content,
        "tts": tts,
        "embeds": embeds
        if embeds is not None
        else [embed]
        if embed is not None
        else None,
        "nonce": nonce,
        "allowed_mentions": allowed_mentions,
        "message_reference": message_reference,
        "sticker_ids": stickers,
        "components": components,
        "flags": flags,
    }
    for key, value in list(payload.items()):
        if key == "tts":
            if not value:
                del payload[key]
        else:
            if value is None:
                del payload[key]
    with client.makes_request(
        Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id),
        json=payload,
    ):
        await client.http.send_message(
            channel_id,
            content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            nonce=nonce,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            stickers=stickers,
            components=components,
            flags=flags,
        )


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
