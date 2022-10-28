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
import sys
from io import BytesIO
from itertools import chain, combinations
from typing import Callable, Iterable, TypeVar

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

import pytest

from discord import File
from discord.types import embed, message, sticker

__all__ = (
    "powerset",
    "random_combination",
    "random_snowflake",
    "random_embed",
    "random_bool",
    "random_allowed_mentions",
    "random_message_reference",
    "random_sticker",
    "random_file",
    "random_count",
    "random_amount",
    "user_id",
    "channel_id",
    "guild_id",
    "message_id",
)

V = TypeVar("V")


def powerset(iterable: Iterable[V]) -> Iterable[Iterable[V]]:
    # https://docs.python.org/3/library/itertools.html#itertools-recipes
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def random_combination(iterable: Iterable[V]) -> Iterable[V]:
    """Generate a random combination of the given iterable.

    Parameters
    ----------
    iterable: Iterable[V]
        The iterable to generate a combination from.

    Returns
    -------
    Iterable[V]
        The generated combination.
    """
    return random.choice(list(powerset(iterable)))


def random_snowflake() -> int:
    """Generate a random snowflake."""
    return random.randint(0, 2**64 - 1)


def random_embed() -> embed.Embed:
    """Generate a random embed object."""
    # TODO: Improve this
    return embed.Embed(
        title="Test",
    )


def random_bool() -> bool:
    """Generate a random boolean."""
    return random.random() > 0.5


def random_allowed_mentions() -> message.AllowedMentions:
    """Generate a random allowed mentions object."""
    parse: list[message.AllowedMentionType] = ["roles", "users", "everyone"]
    return message.AllowedMentions(
        parse=list(random_combination(parse)),
        roles=random_amount(random_snowflake) if random_bool() else None,
        users=random_amount(random_snowflake) if random_bool() else None,
        replied_user=random.random() > 0.5,
    )


def random_message_reference() -> message.MessageReference:
    """Generate a random message reference object."""
    return message.MessageReference(
        message_id=random_snowflake() if random_bool() else None,
        channel_id=random_snowflake() if random_bool() else None,
        guild_id=random_snowflake() if random_bool() else None,
        fail_if_not_exists=random.random() > 0.5 if random_bool() else None,
    )


def random_sticker() -> sticker.StickerItem:
    """Generate a random sticker object."""
    return sticker.StickerItem(
        id=random_snowflake(),
        name="test",
        format_type=random.choice([1, 2, 3]),
    )


def random_file() -> File:  # TODO: Improve random_file helper
    """Generate a random file object."""
    buf = BytesIO(b"test")
    return File(buf, filename="test.txt")


def random_count(maximum: int = 10) -> int:
    """Generate a random number from 1 to ``maximum``, inclusive.

    Parameters
    ----------
    maximum: int
        The maximum number to generate. Defaults to 10.

    ..note::
        This is equivalent to ``random.randint(1, maximum)``.

    Returns
    -------
    int
        The generated number.
    """
    return random.randint(1, maximum)


P = ParamSpec("P")
T = TypeVar("T")


def random_amount(
    func: Callable[P, T], maximum: int = 10, args: P.args = (), kwargs: P.kwargs = None
) -> list[T]:
    """Generate a random amount of the given function.

    Parameters
    ----------
    func: Callable[P, T]
        The function to generate a random amount of.
    maximum: int
        The maximum amount to generate. Defaults to 10.
    *args: P.args
        The arguments to pass to the function.
    **kwargs: P.kwargs
        The keyword arguments to pass to the function.

    Returns
    -------
    list[T]
        The generated list of values.
    """
    if kwargs is None:
        kwargs = {}
    return [func(*args, **kwargs) for _ in range(random_count(maximum))]


def random_dict() -> dict[str, str | int | bool]:
    """Generate a random dictionary."""
    value_type = random.choice([str, int, bool])
    if value_type is str:
        value = "test"  # TODO: Use random string in random_dict
    elif value_type is int:
        value = random.randrange(0, 100)
    else:
        value = random_bool()
    return {  # TODO: Use random string in random_dict keys
        str(random_snowflake()): value for _ in range(random_count())
    }


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


@pytest.fixture
def reason() -> str:
    """A random reason fixture."""
    return "test"  # TODO: Randomize reason fixture
