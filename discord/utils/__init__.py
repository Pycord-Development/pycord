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
from .public import basic_autocomplete, generate_snowflake, utcnow, snowflake_time, oauth_url, Undefined, MISSING

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
    "sleep_until ",
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


def compute_timedelta(dt: datetime.datetime):
    if dt.tzinfo is None:
        dt = dt.astimezone()
    now = datetime.datetime.now(datetime.timezone.utc)
    return max((dt - now).total_seconds(), 0)


def valid_icon_size(size: int) -> bool:
    """Icons must be power of 2 within [16, 4096]."""
    return not size & (size - 1) and 4096 >= size >= 16


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


_MARKDOWN_ESCAPE_SUBREGEX = "|".join(r"\{0}(?=([\s\S]*((?<!\{0})\{0})))".format(c) for c in ("*", "`", "_", "~", "|"))

# regular expression for finding and escaping links in markdown
# note: technically, brackets are allowed in link text.
# perhaps more concerning, parentheses are also allowed in link destination.
# this regular expression matches neither of those.
# this page provides a good reference: http://blog.michaelperrin.fr/2019/02/04/advanced-regular-expressions/
_MARKDOWN_ESCAPE_LINKS = r"""
\[  # matches link text
    [^\[\]]* # link text can contain anything but brackets
\]
\(  # matches link destination
    [^\(\)]+ # link destination cannot contain parentheses
\)"""  # note 2: make sure this regex is consumed in re.X (extended mode) since it has whitespace and comments

_MARKDOWN_ESCAPE_COMMON = rf"^>(?:>>)?\s|{_MARKDOWN_ESCAPE_LINKS}"

_MARKDOWN_ESCAPE_REGEX = re.compile(
    rf"(?P<markdown>{_MARKDOWN_ESCAPE_SUBREGEX}|{_MARKDOWN_ESCAPE_COMMON})",
    re.MULTILINE | re.X,
)

_URL_REGEX = r"(?P<url><[^: >]+:\/[^ >]+>|(?:https?|steam):\/\/[^\s<]+[^<.,:;\"\'\]\s])"

_MARKDOWN_STOCK_REGEX = rf"(?P<markdown>[_\\~|\*`]|{_MARKDOWN_ESCAPE_COMMON})"


def remove_markdown(text: str, *, ignore_links: bool = True) -> str:
    """A helper function that removes markdown characters.

    .. versionadded:: 1.7

    .. note::
            This function is not markdown aware and may remove meaning from the original text. For example,
            if the input contains ``10 * 5`` then it will be converted into ``10  5``.

    Parameters
    ----------
    text: :class:`str`
        The text to remove markdown from.
    ignore_links: :class:`bool`
        Whether to leave links alone when removing markdown. For example,
        if a URL in the text contains characters such as ``_`` then it will
        be left alone. Defaults to ``True``.

    Returns
    -------
    :class:`str`
        The text with the markdown special characters removed.
    """

    def replacement(match):
        groupdict = match.groupdict()
        return groupdict.get("url", "")

    regex = _MARKDOWN_STOCK_REGEX
    if ignore_links:
        regex = f"(?:{_URL_REGEX}|{regex})"
    return re.sub(regex, replacement, text, 0, re.MULTILINE)


def escape_markdown(text: str, *, as_needed: bool = False, ignore_links: bool = True) -> str:
    r"""A helper function that escapes Discord's markdown.

    Parameters
    -----------
    text: :class:`str`
        The text to escape markdown from.
    as_needed: :class:`bool`
        Whether to escape the markdown characters as needed. This
        means that it does not escape extraneous characters if it's
        not necessary, e.g. ``**hello**`` is escaped into ``\*\*hello**``
        instead of ``\*\*hello\*\*``. Note however that this can open
        you up to some clever syntax abuse. Defaults to ``False``.
    ignore_links: :class:`bool`
        Whether to leave links alone when escaping markdown. For example,
        if a URL in the text contains characters such as ``_`` then it will
        be left alone. This option is not supported with ``as_needed``.
        Defaults to ``True``.

    Returns
    --------
    :class:`str`
        The text with the markdown special characters escaped with a slash.
    """

    if not as_needed:

        def replacement(match):
            groupdict = match.groupdict()
            is_url = groupdict.get("url")
            if is_url:
                return is_url
            return f"\\{groupdict['markdown']}"

        regex = _MARKDOWN_STOCK_REGEX
        if ignore_links:
            regex = f"(?:{_URL_REGEX}|{regex})"
        return re.sub(regex, replacement, text, 0, re.MULTILINE | re.X)
    else:
        text = re.sub(r"\\", r"\\\\", text)
        return _MARKDOWN_ESCAPE_REGEX.sub(r"\\\1", text)


def escape_mentions(text: str) -> str:
    """A helper function that escapes everyone, here, role, and user mentions.

    .. note::

        This does not include channel mentions.

    .. note::

        For more granular control over what mentions should be escaped
        within messages, refer to the :class:`~discord.AllowedMentions`
        class.

    Parameters
    ----------
    text: :class:`str`
        The text to escape mentions from.

    Returns
    -------
    :class:`str`
        The text with the mentions removed.
    """
    return re.sub(r"@(everyone|here|[!&]?[0-9]{17,20})", "@\u200b\\1", text)


def raw_mentions(text: str) -> list[int]:
    """Returns a list of user IDs matching ``<@user_id>`` in the string.

    .. versionadded:: 2.2

    Parameters
    ----------
    text: :class:`str`
        The string to get user mentions from.

    Returns
    -------
    List[:class:`int`]
        A list of user IDs found in the string.
    """
    return [int(x) for x in re.findall(r"<@!?([0-9]+)>", text)]


def raw_channel_mentions(text: str) -> list[int]:
    """Returns a list of channel IDs matching ``<@#channel_id>`` in the string.

    .. versionadded:: 2.2

    Parameters
    ----------
    text: :class:`str`
        The string to get channel mentions from.

    Returns
    -------
    List[:class:`int`]
        A list of channel IDs found in the string.
    """
    return [int(x) for x in re.findall(r"<#([0-9]+)>", text)]


def raw_role_mentions(text: str) -> list[int]:
    """Returns a list of role IDs matching ``<@&role_id>`` in the string.

    .. versionadded:: 2.2

    Parameters
    ----------
    text: :class:`str`
        The string to get role mentions from.

    Returns
    -------
    List[:class:`int`]
        A list of role IDs found in the string.
    """
    return [int(x) for x in re.findall(r"<@&([0-9]+)>", text)]


def _chunk(iterator: Iterator[T], max_size: int) -> Iterator[list[T]]:
    ret = []
    n = 0
    for item in iterator:
        ret.append(item)
        n += 1
        if n == max_size:
            yield ret
            ret = []
            n = 0
    if ret:
        yield ret


async def _achunk(iterator: AsyncIterator[T], max_size: int) -> AsyncIterator[list[T]]:
    ret = []
    n = 0
    async for item in iterator:
        ret.append(item)
        n += 1
        if n == max_size:
            yield ret
            ret = []
            n = 0
    if ret:
        yield ret


@overload
def as_chunks(iterator: Iterator[T], max_size: int) -> Iterator[list[T]]: ...


@overload
def as_chunks(iterator: AsyncIterator[T], max_size: int) -> AsyncIterator[list[T]]: ...


def as_chunks(iterator: _Iter[T], max_size: int) -> _Iter[list[T]]:
    """A helper function that collects an iterator into chunks of a given size.

    .. versionadded:: 2.0

    .. warning::

        The last chunk collected may not be as large as ``max_size``.

    Parameters
    ----------
    iterator: Union[:class:`collections.abc.Iterator`, :class:`collections.abc.AsyncIterator`]
        The iterator to chunk, can be sync or async.
    max_size: :class:`int`
        The maximum chunk size.

    Returns
    -------
    Union[:class:`collections.abc.Iterator`, :class:`collections.abc.AsyncIterator`]
        A new iterator which yields chunks of a given size.
    """
    if max_size <= 0:
        raise ValueError("Chunk sizes must be greater than 0.")

    if isinstance(iterator, AsyncIterator):
        return _achunk(iterator, max_size)
    return _chunk(iterator, max_size)


TimestampStyle = Literal["f", "F", "d", "D", "t", "T", "R"]


def format_dt(dt: datetime.datetime | datetime.time, /, style: TimestampStyle | None = None) -> str:
    """A helper function to format a :class:`datetime.datetime` for presentation within Discord.

    This allows for a locale-independent way of presenting data using Discord specific Markdown.

    +-------------+----------------------------+-----------------+
    |    Style    |       Example Output       |   Description   |
    +=============+============================+=================+
    | t           | 22:57                      | Short Time      |
    +-------------+----------------------------+-----------------+
    | T           | 22:57:58                   | Long Time       |
    +-------------+----------------------------+-----------------+
    | d           | 17/05/2016                 | Short Date      |
    +-------------+----------------------------+-----------------+
    | D           | 17 May 2016                | Long Date       |
    +-------------+----------------------------+-----------------+
    | f (default) | 17 May 2016 22:57          | Short Date Time |
    +-------------+----------------------------+-----------------+
    | F           | Tuesday, 17 May 2016 22:57 | Long Date Time  |
    +-------------+----------------------------+-----------------+
    | R           | 5 years ago                | Relative Time   |
    +-------------+----------------------------+-----------------+

    Note that the exact output depends on the user's locale setting in the client. The example output
    presented is using the ``en-GB`` locale.

    .. versionadded:: 2.0

    Parameters
    ----------
    dt: Union[:class:`datetime.datetime`, :class:`datetime.time`]
        The datetime to format.
    style: :class:`str`R
        The style to format the datetime with.

    Returns
    -------
    :class:`str`
        The formatted string.
    """
    if isinstance(dt, datetime.time):
        dt = datetime.datetime.combine(datetime.datetime.now(), dt)
    if style is None:
        return f"<t:{int(dt.timestamp())}>"
    return f"<t:{int(dt.timestamp())}:{style}>"
