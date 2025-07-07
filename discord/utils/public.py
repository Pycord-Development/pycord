from __future__ import annotations

import asyncio
import datetime
from enum import Enum, auto
import itertools
from collections.abc import Awaitable, Callable, Iterable
from typing import TYPE_CHECKING, Any, Literal, Iterable


if TYPE_CHECKING:
    from .abc import Snowflake
    from ..commands.context import AutocompleteContext
    from ..commands.options import OptionChoice
    from ..permissions import Permissions


class Undefined(Enum):
    MISSING = auto()

    def __bool__(self) -> Literal[False]:
        return False


MISSING: Literal[Undefined.MISSING] = Undefined.MISSING

DISCORD_EPOCH = 1420070400000


def utcnow() -> datetime.datetime:
    """A helper function to return an aware UTC datetime representing the current time.

    This should be preferred to :meth:`datetime.datetime.utcnow` since it is an aware
    datetime, compared to the naive datetime in the standard library.

    .. versionadded:: 2.0

    Returns
    -------
    :class:`datetime.datetime`
        The current aware datetime in UTC.
    """
    return datetime.datetime.now(datetime.timezone.utc)


V = Iterable["OptionChoice"] | Iterable[str] | Iterable[int] | Iterable[float]
AV = Awaitable[V]
Values = V | Callable[["AutocompleteContext"], V | AV] | AV
AutocompleteFunc = Callable[["AutocompleteContext"], AV]
FilterFunc = Callable[["AutocompleteContext", Any], bool | Awaitable[bool]]


def basic_autocomplete(values: Values, *, filter: FilterFunc | None = None) -> AutocompleteFunc:
    """A helper function to make a basic autocomplete for slash commands. This is a pretty standard autocomplete and
    will return any options that start with the value from the user, case-insensitive. If the ``values`` parameter is
    callable, it will be called with the AutocompleteContext.

    This is meant to be passed into the :attr:`discord.Option.autocomplete` attribute.

    Parameters
    ----------
    values: Union[Union[Iterable[:class:`.OptionChoice`], Iterable[:class:`str`], Iterable[:class:`int`], Iterable[:class:`float`]], Callable[[:class:`.AutocompleteContext`], Union[Union[Iterable[:class:`str`], Iterable[:class:`int`], Iterable[:class:`float`]], Awaitable[Union[Iterable[:class:`str`], Iterable[:class:`int`], Iterable[:class:`float`]]]]], Awaitable[Union[Iterable[:class:`str`], Iterable[:class:`int`], Iterable[:class:`float`]]]]
        Possible values for the option. Accepts an iterable of :class:`str`, a callable (sync or async) that takes a
        single argument of :class:`.AutocompleteContext`, or a coroutine. Must resolve to an iterable of :class:`str`.
    filter: Optional[Callable[[:class:`.AutocompleteContext`, Any], Union[:class:`bool`, Awaitable[:class:`bool`]]]]
        An optional callable (sync or async) used to filter the autocomplete options. It accepts two arguments:
        the :class:`.AutocompleteContext` and an item from ``values`` iteration treated as callback parameters. If ``None`` is provided, a default filter is used that includes items whose string representation starts with the user's input value, case-insensitive.

        .. versionadded:: 2.7

    Returns
    -------
    Callable[[:class:`.AutocompleteContext`], Awaitable[Union[Iterable[:class:`.OptionChoice`], Iterable[:class:`str`], Iterable[:class:`int`], Iterable[:class:`float`]]]]
        A wrapped callback for the autocomplete.

    Examples
    --------

    Basic usage:

    .. code-block:: python3

        Option(str, "color", autocomplete=basic_autocomplete(("red", "green", "blue")))

        # or


        async def autocomplete(ctx):
            return "foo", "bar", "baz", ctx.interaction.user.name


        Option(str, "name", autocomplete=basic_autocomplete(autocomplete))

    With filter parameter:

    .. code-block:: python3

        Option(
            str,
            "color",
            autocomplete=basic_autocomplete(("red", "green", "blue"), filter=lambda c, i: str(c.value or "") in i),
        )

    .. versionadded:: 2.0

    Note
    ----
    Autocomplete cannot be used for options that have specified choices.
    """

    async def autocomplete_callback(ctx: AutocompleteContext) -> V:
        _values = values  # since we reassign later, python considers it local if we don't do this

        if callable(_values):
            _values = _values(ctx)
        if asyncio.iscoroutine(_values):
            _values = await _values

        if filter is None:

            def _filter(ctx: AutocompleteContext, item: Any) -> bool:
                item = getattr(item, "name", item)
                return str(item).lower().startswith(str(ctx.value or "").lower())

            gen = (val for val in _values if _filter(ctx, val))

        elif asyncio.iscoroutinefunction(filter):
            gen = (val for val in _values if await filter(ctx, val))

        elif callable(filter):
            gen = (val for val in _values if filter(ctx, val))

        else:
            raise TypeError("``filter`` must be callable.")

        return iter(itertools.islice(gen, 25))

    return autocomplete_callback


def generate_snowflake(
    dt: datetime.datetime | None = None,
    *,
    mode: Literal["boundary", "realistic"] = "boundary",
    high: bool = False,
) -> int:
    """Returns a numeric snowflake pretending to be created at the given date.

    This function can generate both realistic snowflakes (for general use) and
    boundary snowflakes (for range queries).

    Parameters
    ----------
    dt: :class:`datetime.datetime`
        A datetime object to convert to a snowflake.
        If naive, the timezone is assumed to be local time.
        If None, uses current UTC time.
    mode: :class:`str`
        The type of snowflake to generate:
        - "realistic": Creates a snowflake with random-like lower bits
        - "boundary": Creates a snowflake for range queries (default)
    high: :class:`bool`
        Only used when mode="boundary". Whether to set the lower 22 bits
        to high (True) or low (False). Default is False.

    Returns
    -------
    :class:`int`
        The snowflake representing the time given.

    Examples
    --------
    # Generate realistic snowflake
    snowflake = generate_snowflake(dt)

    # Generate boundary snowflakes
    lower_bound = generate_snowflake(dt, mode="boundary", high=False)
    upper_bound = generate_snowflake(dt, mode="boundary", high=True)

    # For inclusive ranges:
    # Lower: generate_snowflake(dt, mode="boundary", high=False) - 1
    # Upper: generate_snowflake(dt, mode="boundary", high=True) + 1
    """
    dt = dt or utcnow()
    discord_millis = int(dt.timestamp() * 1000 - DISCORD_EPOCH)

    if mode == "realistic":
        return (discord_millis << 22) | 0x3FFFFF
    elif mode == "boundary":
        return (discord_millis << 22) + (2**22 - 1 if high else 0)
    else:
        raise ValueError(f"Invalid mode '{mode}'. Must be 'realistic' or 'boundary'")


def snowflake_time(id: int) -> datetime.datetime:
    """Converts a Discord snowflake ID to a UTC-aware datetime object.

    Parameters
    ----------
    id: :class:`int`
        The snowflake ID.

    Returns
    -------
    :class:`datetime.datetime`
        An aware datetime in UTC representing the creation time of the snowflake.
    """
    timestamp = ((id >> 22) + DISCORD_EPOCH) / 1000
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)


def oauth_url(
    client_id: int | str,
    *,
    permissions: Permissions | Undefined = MISSING,
    guild: Snowflake | Undefined = MISSING,
    redirect_uri: str | Undefined = MISSING,
    scopes: Iterable[str] | Undefined = MISSING,
    disable_guild_select: bool = False,
) -> str:
    """A helper function that returns the OAuth2 URL for inviting the bot
    into guilds.

    Parameters
    ----------
    client_id: Union[:class:`int`, :class:`str`]
        The client ID for your bot.
    permissions: :class:`~discord.Permissions`
        The permissions you're requesting. If not given then you won't be requesting any
        permissions.
    guild: :class:`~discord.abc.Snowflake`
        The guild to pre-select in the authorization screen, if available.
    redirect_uri: :class:`str`
        An optional valid redirect URI.
    scopes: Iterable[:class:`str`]
        An optional valid list of scopes. Defaults to ``('bot',)``.

        .. versionadded:: 1.7
    disable_guild_select: :class:`bool`
        Whether to disallow the user from changing the guild dropdown.

        .. versionadded:: 2.0

    Returns
    -------
    :class:`str`
        The OAuth2 URL for inviting the bot into guilds.
    """
    url = f"https://discord.com/oauth2/authorize?client_id={client_id}"
    url += f"&scope={'+'.join(scopes or ('bot',))}"
    if permissions is not MISSING:
        url += f"&permissions={permissions.value}"
    if guild is not MISSING:
        url += f"&guild_id={guild.id}"
    if redirect_uri is not MISSING:
        from urllib.parse import urlencode

        url += f"&response_type=code&{urlencode({'redirect_uri': redirect_uri})}"
    if disable_guild_select:
        url += "&disable_guild_select=true"
    return url


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
