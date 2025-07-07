"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
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

import array
import collections.abc
import datetime
import json
import re
from bisect import bisect_left
from inspect import signature as _signature
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Callable,
    Generic,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    Protocol,
    Sequence,
    TypeVar,
    Union,
    overload,
)

from ..errors import HTTPException
from .public import (
    basic_autocomplete,
    generate_snowflake,
    utcnow,
    snowflake_time,
    oauth_url,
    Undefined,
    MISSING,
    format_dt,
    escape_mentions,
    raw_mentions,
    raw_channel_mentions,
    raw_mentions,
    remove_markdown,
    escape_markdown,
)

try:
    import msgspec
except ModuleNotFoundError:
    HAS_MSGSPEC = False
else:
    HAS_MSGSPEC = True

DISCORD_EPOCH = 1420070400000


__all__ = (
    "oauth_url",
    "snowflake_time",
    "find",
    "get_or_fetch",
    "utcnow",
    "remove_markdown",
    "escape_markdown",
    "escape_mentions",
    "raw_mentions",
    "raw_channel_mentions",
    "raw_role_mentions",
    "as_chunks",
    "format_dt",
    "generate_snowflake",
    "basic_autocomplete",
    "Undefined",
    "MISSING",
)


class _cached_property:
    def __init__(self, function):
        self.function = function
        self.__doc__ = getattr(function, "__doc__")

    def __get__(self, instance, owner):
        if instance is None:
            return self

        value = self.function(instance)
        setattr(instance, self.function.__name__, value)

        return value


if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    class _RequestLike(Protocol):
        headers: Mapping[str, Any]

    cached_property = property

    P = ParamSpec("P")

else:
    cached_property = _cached_property
    AutocompleteContext = Any
    OptionChoice = Any


T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
_Iter = Union[Iterator[T], AsyncIterator[T]]


class CachedSlotProperty(Generic[T, T_co]):
    def __init__(self, name: str, function: Callable[[T], T_co]) -> None:
        self.name = name
        self.function = function
        self.__doc__ = getattr(function, "__doc__")

    @overload
    def __get__(self, instance: None, owner: type[T]) -> CachedSlotProperty[T, T_co]: ...

    @overload
    def __get__(self, instance: T, owner: type[T]) -> T_co: ...

    def __get__(self, instance: T | None, owner: type[T]) -> Any:
        if instance is None:
            return self

        try:
            return getattr(instance, self.name)
        except AttributeError:
            value = self.function(instance)
            setattr(instance, self.name, value)
            return value


class classproperty(Generic[T_co]):
    def __init__(self, fget: Callable[[Any], T_co]) -> None:
        self.fget = fget

    def __get__(self, instance: Any | None, owner: type[Any]) -> T_co:
        return self.fget(owner)

    def __set__(self, instance, value) -> None:
        raise AttributeError("cannot set attribute")


def cached_slot_property(
    name: str,
) -> Callable[[Callable[[T], T_co]], CachedSlotProperty[T, T_co]]:
    def decorator(func: Callable[[T], T_co]) -> CachedSlotProperty[T, T_co]:
        return CachedSlotProperty(name, func)

    return decorator


class SequenceProxy(Generic[T_co], collections.abc.Sequence):
    """Read-only proxy of a Sequence."""

    def __init__(self, proxied: Sequence[T_co]):
        self.__proxied = proxied

    def __getitem__(self, idx: int) -> T_co:
        return self.__proxied[idx]

    def __len__(self) -> int:
        return len(self.__proxied)

    def __contains__(self, item: Any) -> bool:
        return item in self.__proxied

    def __iter__(self) -> Iterator[T_co]:
        return iter(self.__proxied)

    def __reversed__(self) -> Iterator[T_co]:
        return reversed(self.__proxied)

    def index(self, value: Any, *args, **kwargs) -> int:
        return self.__proxied.index(value, *args, **kwargs)

    def count(self, value: Any) -> int:
        return self.__proxied.count(value)


def copy_doc(original: Callable) -> Callable[[T], T]:
    def decorator(overridden: T) -> T:
        overridden.__doc__ = original.__doc__
        overridden.__signature__ = _signature(original)  # type: ignore
        return overridden

    return decorator


def find(predicate: Callable[[T], Any], seq: Iterable[T]) -> T | None:
    """A helper to return the first element found in the sequence
    that meets the predicate. For example: ::

        member = discord.utils.find(lambda m: m.name == "Mighty", channel.guild.members)

    would find the first :class:`~discord.Member` whose name is 'Mighty' and return it.
    If an entry is not found, then ``None`` is returned.

    This is different from :func:`py:filter` due to the fact it stops the moment it finds
    a valid entry.

    Parameters
    ----------
    predicate
        A function that returns a boolean-like result.
    seq: :class:`collections.abc.Iterable`
        The iterable to search through.
    """

    for element in seq:
        if predicate(element):
            return element
    return None


async def get_or_fetch(obj, attr: str, id: int, *, default: Any = MISSING) -> Any:
    """|coro|

    Attempts to get an attribute from the object in cache. If it fails, it will attempt to fetch it.
    If the fetch also fails, an error will be raised.

    Parameters
    ----------
    obj: Any
        The object to use the get or fetch methods in
    attr: :class:`str`
        The attribute to get or fetch. Note the object must have both a ``get_`` and ``fetch_`` method for this attribute.
    id: :class:`int`
        The ID of the object
    default: Any
        The default value to return if the object is not found, instead of raising an error.

    Returns
    -------
    Any
        The object found or the default value.

    Raises
    ------
    :exc:`AttributeError`
        The object is missing a ``get_`` or ``fetch_`` method
    :exc:`NotFound`
        Invalid ID for the object
    :exc:`HTTPException`
        An error occurred fetching the object
    :exc:`Forbidden`
        You do not have permission to fetch the object

    Examples
    --------

    Getting a guild from a guild ID: ::

        guild = await utils.get_or_fetch(client, "guild", guild_id)

    Getting a channel from the guild. If the channel is not found, return None: ::

        channel = await utils.get_or_fetch(guild, "channel", channel_id, default=None)
    """
    getter = getattr(obj, f"get_{attr}")(id)
    if getter is None:
        try:
            getter = await getattr(obj, f"fetch_{attr}")(id)
        except AttributeError:
            getter = await getattr(obj, f"_fetch_{attr}")(id)
            if getter is None:
                raise ValueError(f"Could not find {attr} with id {id} on {obj}")
        except (HTTPException, ValueError):
            if default is not MISSING:
                return default
            else:
                raise
    return getter


if HAS_MSGSPEC:

    def _to_json(obj: Any) -> str:  # type: ignore
        return msgspec.json.encode(obj).decode("utf-8")

    _from_json = msgspec.json.decode  # type: ignore

else:

    def _to_json(obj: Any) -> str:
        return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)

    _from_json = json.loads


def get_slots(cls: type[Any]) -> Iterator[str]:
    for mro in reversed(cls.__mro__):
        try:
            yield from mro.__slots__
        except AttributeError:
            continue


class SnowflakeList(array.array):
    """Internal data storage class to efficiently store a list of snowflakes.

    This should have the following characteristics:

    - Low memory usage
    - O(n) iteration (obviously)
    - O(n log n) initial creation if data is unsorted
    - O(log n) search and indexing
    - O(n) insertion
    """

    __slots__ = ()

    if TYPE_CHECKING:

        def __init__(self, data: Iterable[int], *, is_sorted: bool = False): ...

    def __new__(cls, data: Iterable[int], *, is_sorted: bool = False):
        return array.array.__new__(cls, "Q", data if is_sorted else sorted(data))  # type: ignore

    def add(self, element: int) -> None:
        i = bisect_left(self, element)
        self.insert(i, element)

    def get(self, element: int) -> int | None:
        i = bisect_left(self, element)
        return self[i] if i != len(self) and self[i] == element else None

    def has(self, element: int) -> bool:
        i = bisect_left(self, element)
        return i != len(self) and self[i] == element
