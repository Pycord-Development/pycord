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
import string
import sys
from io import BytesIO
from itertools import chain, combinations
from typing import Callable, Iterable, TypeVar, get_args

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

import pytest

from discord import File
from discord.types import channel
from discord.types import embed as embed_type
from discord.types import guild, message, sticker, threads

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
    "random_overwrite",
    "random_dict",
    "random_archive_duration",
    "random_bytes",
    "random_string",
    "user_id",
    "channel_id",
    "guild_id",
    "message_id",
    "emoji",
    "limit",
    "after",
    "before",
    "around",
    "reason",
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


def random_embed() -> embed_type.Embed:
    """Generate a random embed object."""
    # TODO: Improve this
    return embed_type.Embed(
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


def random_file(filename: str = "test.txt") -> File:  # TODO: Improve random_file helper
    """Generate a random file object."""
    buf = BytesIO(random_bytes())
    return File(buf, filename=filename)


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


def random_dict(*, keys: Iterable[str] | None = None) -> dict[str, str | int | bool]:
    """Generate a random dictionary."""
    T = TypeVar("T", str, int, bool)
    value_type: T = random.choice([str, int, bool])

    def value(key: str) -> T:
        if value_type is str:
            return f"value test{key}"
        elif value_type is int:
            return random.randrange(0, 100)
        elif value_type is bool:
            return random_bool()
        else:
            raise TypeError(f"Unknown value type: {value_type}")

    if keys is None:
        keys = [f"test{i}" for i in range(random_count())]
    return {random_string(): value(key) for key in keys}


def random_overwrite() -> channel.PermissionOverwrite:
    """Generate a random overwrite."""
    return channel.PermissionOverwrite(
        id=random_snowflake(),
        type=random.choice(get_args(channel.OverwriteType)),
        allow=str(random_snowflake()),
        deny=str(random_snowflake()),
    )


def random_archive_duration() -> threads.ThreadArchiveDuration:
    """Generate a random archive duration."""
    return random.choice(get_args(threads.ThreadArchiveDuration))


def random_bytes(length: int = 10) -> bytes:
    """Generate random bytes"""
    return random_string(length).encode()


def random_string(length: int = 10) -> str:
    """Generate a random string"""
    letters = string.ascii_letters + string.digits  # + string.punctuation
    return "".join(random.choices(list(letters), k=length))


def random_snowflake_list() -> list[int]:
    return random_amount(random_snowflake)


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
def emoji() -> str:
    """A random emoji fixture."""
    return "👍"  # TODO: Randomize emoji fixture


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
def applied_tags(request) -> list[int] | None:
    if request.param == "random":
        return random_snowflake_list()
    return None
