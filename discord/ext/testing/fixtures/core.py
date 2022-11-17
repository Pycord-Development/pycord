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

from discord.types import components
from discord.types import embed as embed_type
from discord.types import message, sticker

from ..helpers import (
    random_allowed_mentions,
    random_amount,
    random_bool,
    random_bytes,
    random_embed,
    random_snowflake,
    random_snowflake_list,
    random_sticker,
    random_string,
)

__all__ = (
    "user_id",
    "channel_id",
    "guild_id",
    "message_id",
    "message_ids",
    "reason",
    "limit",
    "after",
    "before",
    "around",
    "emoji",
    "name",
    "invitable",
    "content",
    "embed",
    "embeds",
    "nonce",
    "allowed_mentions",
    "stickers",
    "components",
    "avatar",
    "applied_tags",
    "icon",
)


@pytest.fixture
def user_id() -> int:
    """A random user ID fixture."""
    return random_snowflake()


@pytest.fixture
def channel_id() -> int:
    """A random channel ID fixture."""
    return random_snowflake()


@pytest.fixture
def guild_id() -> int:
    """A random guild ID fixture."""
    return random_snowflake()


@pytest.fixture
def message_id() -> int:
    """A random message ID fixture."""
    return random_snowflake()


@pytest.fixture
def message_ids() -> list[int]:
    """A random amount of message IDs fixture."""
    return random_amount(random_snowflake)


@pytest.fixture(params=[None, "random"])
def reason(request) -> str:
    """A random reason fixture."""
    if request.param == "random":
        return random_string()
    return request.param


@pytest.fixture
def limit() -> int:
    """A random limit fixture."""
    return random.randrange(0, 1000)


@pytest.fixture(params=(None, "random"))
def after(request) -> int | None:
    """A random after fixture."""
    if request.param == "random":
        return random_snowflake()
    return None


@pytest.fixture(params=(None, "random"))
def before(request) -> int | None:
    """A random before fixture."""
    if request.param == "random":
        return random_snowflake()
    return None


@pytest.fixture(params=(None, "random"))
def around(request) -> int | None:
    """A random around fixture."""
    if request.param == "random":
        return random_snowflake()
    return None


@pytest.fixture
def emoji() -> str:
    """A random emoji fixture."""
    return "👍"  # TODO: Randomize emoji fixture


@pytest.fixture
def name() -> str | None:
    return random_string()


@pytest.fixture
def invitable() -> bool:
    # Only checks one case to shorten tests
    return random_bool()


@pytest.fixture(params=(None, "random"))
def content(request) -> str | None:
    if request.param == "random":
        return random_string()
    return None


@pytest.fixture(name="embed", params=(None, random_embed()))
def embed(request) -> embed_type.Embed | None:
    return request.param


@pytest.fixture(params=(None, random_amount(random_embed)))
def embeds(request) -> list[embed_type.Embed] | None:
    return request.param


@pytest.fixture(params=(None, "..."))  # TODO: Replace string value
def nonce(request) -> str | None:
    return request.param


@pytest.fixture(params=(None, random_allowed_mentions()))
def allowed_mentions(request) -> message.AllowedMentions | None:
    return request.param


@pytest.fixture(params=(None, [], random_amount(random_sticker)))
def stickers(request) -> list[sticker.StickerItem] | None:
    return request.param


@pytest.fixture(params=(None,))  # TODO: Add components to tests
def components(request) -> components.Component | None:
    return request.param


@pytest.fixture(params=(None, "random"))
def avatar(request) -> bytes | None:
    if request.param == "random":
        return random_bytes()
    return None


@pytest.fixture(params=(None, "random"))
def icon(request) -> bytes | None:
    """A random icon fixture"""
    if request.param == "random":
        return random_bytes()
    return None


@pytest.fixture(params=(None, "random"))
def applied_tags(request) -> list[int] | None:
    if request.param == "random":
        return random_snowflake_list()
    return None
