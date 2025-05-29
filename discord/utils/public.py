import asyncio
import itertools
from typing import TYPE_CHECKING, Literal
from collections.abc import Iterable, Callable, Awaitable
from typing import Any
import datetime

if TYPE_CHECKING:
    from ..commands.context import AutocompleteContext
    from ..commands.options import OptionChoice

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
    dt: datetime.datetime | None = None, *, mode: Literal["boundary", "realistic"] = "boundary", high: bool = False
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
        - "realistic": Creates a snowflake with random-like lower bits (default)
        - "boundary": Creates a snowflake for range queries
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
