import random
from itertools import chain, combinations
from typing import Iterable, TypeVar

import pytest

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
    "user_id",
    "channel_id",
)

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
