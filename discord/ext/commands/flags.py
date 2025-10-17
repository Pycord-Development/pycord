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

import inspect
import re
import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Iterator, Literal, Pattern, TypeVar, Union

from discord.utils import (
    MISSING,
    maybe_coroutine,
    resolve_annotation,
)

from .converter import run_converters
from .errors import (
    BadFlagArgument,
    CommandError,
    MissingFlagArgument,
    MissingRequiredFlag,
    TooManyFlags,
)
from .view import StringView

__all__ = (
    "Flag",
    "flag",
    "FlagConverter",
)

# Typing helpers for the MISSING sentinel (no runtime behavior change)
# We give type-checkers a concrete Missing type and a generic Maybe[T] = T | Missing
# without requiring changes to discord.utils.
if TYPE_CHECKING:
    from .context import Context
    class _MissingType:  # only exists for type-checkers
        ...
    Missing = _MissingType
else:
    # at runtime we don't care; this keeps annotations import-safe
    Missing = type(MISSING)

T = TypeVar("T")
Maybe = Union[T, Missing]


def _missing_field_factory() -> field:
    return field(default_factory=lambda: MISSING)


@dataclass
class Flag:
    """Represents a flag parameter for :class:`FlagConverter`.

    The :func:`~discord.ext.commands.flag` function helps
    create these flag objects, but it is not necessary to
    do so. These cannot be constructed manually.

    Attributes
    ----------
    name: :class:`str`
        The name of the flag.
    aliases: List[:class:`str`]
        The aliases of the flag name.
    attribute: :class:`str`
        The attribute in the class that corresponds to this flag.
    default: Any
        The default value of the flag, if available.
    annotation: Any
        The underlying evaluated annotation of the flag.
    max_args: :class:`int`
        The maximum number of arguments the flag can accept.
        A negative value indicates an unlimited amount of arguments.
    override: :class:`bool`
        Whether multiple given values overrides the previous value.
    """

    # NOTE: Fields that can be the sentinel are typed as Maybe[...]
    name: Maybe[str] = _missing_field_factory()
    aliases: list[str] = field(default_factory=list)
    attribute: Maybe[str] = _missing_field_factory()
    annotation: Maybe[Any] = _missing_field_factory()
    default: Maybe[Any] = _missing_field_factory()
    max_args: Maybe[int] = _missing_field_factory()
    override: Maybe[bool] = _missing_field_factory()
    cast_to_dict: bool = False

    @property
    def required(self) -> bool:
        """Whether the flag is required.

        A required flag has no default value.
        """
        return self.default is MISSING


def flag(
    *,
    name: Maybe[str] = MISSING,
    aliases: Maybe[list[str]] = MISSING,
    default: Maybe[Any] = MISSING,
    max_args: Maybe[int] = MISSING,
    override: Maybe[bool] = MISSING,
) -> Any:
    """Override default functionality and parameters of the underlying :class:`FlagConverter`
    class attributes.

    Parameters
    ----------
    name: :class:`str`
        The flag name. If not given, defaults to the attribute name.
    aliases: List[:class:`str`]
        Aliases to the flag name. If not given, no aliases are set.
    default: Any
        The default parameter. This could be either a value or a callable that takes
        :class:`Context` as its sole parameter. If not given then it defaults to
        the default value given to the attribute.
    max_args: :class:`int`
        The maximum number of arguments the flag can accept.
        A negative value indicates an unlimited amount of arguments.
        The default value depends on the annotation given.
    override: :class:`bool`
        Whether multiple given values overrides the previous value. The default
        value depends on the annotation given.
    """
    return Flag(
        name=name,
        aliases=aliases if aliases is not MISSING else MISSING,  # keep old behavior
        default=default,
        max_args=max_args,
        override=override,
    )


def validate_flag_name(name: str, forbidden: set[str]):
    if not name:
        raise ValueError("flag names should not be empty")

    for ch in name:
        if ch.isspace():
            raise ValueError(f"flag name {name!r} cannot have spaces")
        if ch == "\\":
            raise ValueError(f"flag name {name!r} cannot have backslashes")
        if ch in forbidden:
            raise ValueError(
                f"flag name {name!r} cannot have any of {forbidden!r} within them"
            )


def get_flags(
    namespace: dict[str, Any], globals: dict[str, Any], locals: dict[str, Any]
) -> dict[str, Flag]:
    annotations = namespace.get("__annotations__", {})
    case_insensitive = namespace["__commands_flag_case_insensitive__"]
    flags: dict[str, Flag] = {}
    cache: dict[str, Any] = {}
    names: set[str] = set()
    for name, annotation in annotations.items():
        flag = namespace.pop(name, MISSING)
        if isinstance(flag, Flag):
            flag.annotation = annotation
        else:
            flag = Flag(name=name, annotation=annotation, default=flag)

        flag.attribute = name
        if flag.name is MISSING:
            flag.name = name

        annotation = flag.annotation = resolve_annotation(
            flag.annotation, globals, locals, cache
        )

        if (
            flag.default is MISSING
            and hasattr(annotation, "__commands_is_flag__")
            and annotation._can_be_constructible()
        ):
            flag.default = annotation._construct_default

        if flag.aliases is MISSING:
            flag.aliases = []

        # Add sensible defaults based off of the type annotation
        # <type> -> (max_args=1)
        # List[str] -> (max_args=-1)
        # Tuple[int, ...] -> (max_args=1)
        # Dict[K, V] -> (max_args=-1, override=True)
        # Union[str, int] -> (max_args=1)
        # Optional[str] -> (default=None, max_args=1)

        try:
            origin = annotation.__origin__
        except AttributeError:
            # A regular type hint
            if flag.max_args is MISSING:
                flag.max_args = 1
        else:
            if origin is Union:
                # typing.Union
                if flag.max_args is MISSING:
                    flag.max_args = 1
                if annotation.__args__[-1] is type(None) and flag.default is MISSING:
                    # typing.Optional
                    flag.default = None
            elif origin is tuple:
                # typing.Tuple
                # tuple parsing is e.g. `flag: peter 20`
                # for Tuple[str, int] would give you flag: ('peter', 20)
                if flag.max_args is MISSING:
                    flag.max_args = 1
            elif origin is list:
                # typing.List
                if flag.max_args is MISSING:
                    flag.max_args = -1
            elif origin is dict:
                # typing.Dict[K, V]
                # Equivalent to:
                # typing.List[typing.Tuple[K, V]]
                flag.cast_to_dict = True
                if flag.max_args is MISSING:
                    flag.max_args = -1
                if flag.override is MISSING:
                    flag.override = True
            elif origin is Literal:
                if flag.max_args is MISSING:
                    flag.max_args = 1
            else:
                raise TypeError(
                    f"Unsupported typing annotation {annotation!r} for"
                    f" {flag.name!r} flag"
                )

        if flag.override is MISSING:
            flag.override = False

        # Validate flag names are unique
        name_key = flag.name.casefold() if case_insensitive else flag.name
        if name_key in names:
            raise TypeError(
                f"{flag.name!r} flag conflicts with previous flag or alias."
            )
        else:
            names.add(name_key)

        for alias in flag.aliases:
            # Validate alias is unique
            alias_key = alias.casefold() if case_insensitive else alias
            if alias_key in names:
                raise TypeError(
                    f"{flag.name!r} flag alias {alias!r} conflicts with previous flag"
                    " or alias."
                )
            else:
                names.add(alias_key)

        flags[flag.name] = flag

    return flags


class FlagsMeta(type):
    if TYPE_CHECKING:
        __commands_is_flag__: bool
        __commands_flags__: dict[str, Flag]
        __commands_flag_aliases__: dict[str, str]
        __commands_flag_regex__: Pattern[str]
        __commands_flag_case_insensitive__: bool
        __commands_flag_delimiter__: str
        __commands_flag_prefix__: str

    def __new__(
        cls: type[type],
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, Any],
        *,
        case_insensitive: Maybe[bool] = MISSING,
        delimiter: Maybe[str] = MISSING,
        prefix: Maybe[str] = MISSING,
    ):
        attrs["__commands_is_flag__"] = True

        try:
            global_ns = sys.modules[attrs["__module__"]].__dict__
        except KeyError:
            global_ns = {}

        frame = inspect.currentframe()
        try:
            if frame is None:
                local_ns = {}
            else:
                if frame.f_back is None:
                    local_ns = frame.f_locals
                else:
                    local_ns = frame.f_back.f_locals
        finally:
            del frame

        flags: dict[str, Flag] = {}
        aliases: dict[str, str] = {}
        for base in reversed(bases):
            if base.__dict__.get("__commands_is_flag__", False):
                flags.update(base.__dict__["__commands_flags__"])
                aliases.update(base.__dict__["__commands_flag_aliases__"])
                if case_insensitive is MISSING:
                    attrs["__commands_flag_case_insensitive__"] = base.__dict__[
                        "__commands_flag_case_insensitive__"
                    ]
                if delimiter is MISSING:
                    attrs["__commands_flag_delimiter__"] = base.__dict__[
                        "__commands_flag_delimiter__"
                    ]
                if prefix is MISSING:
                    attrs["__commands_flag_prefix__"] = base.__dict__[
                        "__commands_flag_prefix__"
                    ]

        if case_insensitive is not MISSING:
            attrs["__commands_flag_case_insensitive__"] = case_insensitive  # type: ignore[assignment]
        if delimiter is not MISSING:
            attrs["__commands_flag_delimiter__"] = delimiter  # type: ignore[assignment]
        if prefix is not MISSING:
            attrs["__commands_flag_prefix__"] = prefix  # type: ignore[assignment]

        case_insensitive_val = attrs.setdefault("__commands_flag_case_insensitive__", False)
        delimiter_val = attrs.setdefault("__commands_flag_delimiter__", ":")
        prefix_val = attrs.setdefault("__commands_flag_prefix__", "")

        for flag_name, flg in get_flags(attrs, global_ns, local_ns).items():
            flags[flag_name] = flg
            aliases.update({alias_name: flag_name for alias_name in flg.aliases})

        forbidden = set(delimiter_val).union(prefix_val)
        for flag_name in flags:
            validate_flag_name(flag_name, forbidden)
        for alias_name in aliases:
            validate_flag_name(alias_name, forbidden)

        regex_flags = 0
        if case_insensitive_val:
            flags = {key.casefold(): value for key, value in flags.items()}
            aliases = {
                key.casefold(): value.casefold() for key, value in aliases.items()
            }
            regex_flags = re.IGNORECASE

        keys = [re.escape(k) for k in flags]
        keys.extend(re.escape(a) for a in aliases)
        keys = sorted(keys, key=len, reverse=True)

        joined = "|".join(keys)
        pattern = re.compile(
            f"(({re.escape(prefix_val)})(?P<flag>{joined}){re.escape(delimiter_val)})",
            regex_flags,
        )
        attrs["__commands_flag_regex__"] = pattern
        attrs["__commands_flags__"] = flags
        attrs["__commands_flag_aliases__"] = aliases

        return type.__new__(cls, name, bases, attrs)


async def tuple_convert_all(
    ctx: "Context", argument: str, flag: Flag, converter: Any
) -> tuple[Any, ...]:
    view = StringView(argument)
    results = []
    param: inspect.Parameter = ctx.current_parameter  # type: ignore
    while not view.eof:
        view.skip_ws()
        if view.eof:
            break

        word = view.get_quoted_word()
        if word is None:
            break

        try:
            converted = await run_converters(ctx, converter, word, param)
        except CommandError:
            raise
        except Exception as e:
            raise BadFlagArgument(flag) from e
        else:
            results.append(converted)

    return tuple(results)


async def tuple_convert_flag(
    ctx: "Context", argument: str, flag: Flag, converters: Any
) -> tuple[Any, ...]:
    view = StringView(argument)
    results = []
    param: inspect.Parameter = ctx.current_parameter  # type: ignore
    for converter in converters:
        view.skip_ws()
        if view.eof:
            break

        word = view.get_quoted_word()
        if word is None:
            break

        try:
            converted = await run_converters(ctx, converter, word, param)
        except CommandError:
            raise
        except Exception as e:
            raise BadFlagArgument(flag) from e
        else:
            results.append(converted)

    if len(results) != len(converters):
        raise BadFlagArgument(flag)

    return tuple(results)


async def convert_flag(ctx, argument: str, flag: Flag, annotation: Any = None) -> Any:
    param: inspect.Parameter = ctx.current_parameter  # type: ignore
    annotation = annotation or flag.annotation
    try:
        origin = annotation.__origin__
    except AttributeError:
        pass
    else:
        if origin is tuple:
            if annotation.__args__[-1] is Ellipsis:
                return await tuple_convert_all(
                    ctx, argument, flag, annotation.__args__[0]
                )
            else:
                return await tuple_convert_flag(
                    ctx, argument, flag, annotation.__args__
                )
        elif origin is list:
            # typing.List[x]
            annotation = annotation.__args__[0]
            return await convert_flag(ctx, argument, flag, annotation)
        elif origin is Union and annotation.__args__[-1] is type(None):
            # typing.Optional[x]
            annotation = Union[annotation.__args__[:-1]]  # type: ignore[index]
            return await run_converters(ctx, annotation, argument, param)
        elif origin is dict:
            # typing.Dict[K, V] -> typing.Tuple[K, V]
            return await tuple_convert_flag(ctx, argument, flag, annotation.__args__)

    try:
        return await run_converters(ctx, annotation, argument, param)
    except CommandError:
        raise
    except Exception as e:
        raise BadFlagArgument(flag) from e


F = TypeVar("F", bound="FlagConverter")


class FlagConverter(metaclass=FlagsMeta):
    """A converter that allows for a user-friendly flag syntax.

    The flags are defined using :pep:`526` type annotations similar
    to the :mod:`dataclasses` Python module. For more information on
    how this converter works, check the appropriate
    :ref:`documentation <ext_commands_flag_converter>`.

    .. container:: operations

        .. describe:: iter(x)

            Returns an iterator of ``(flag_name, flag_value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.

    .. versionadded:: 2.0

    Parameters
    ----------
    case_insensitive: :class:`bool`
        A class parameter to toggle case insensitivity of the flag parsing.
        If ``True`` then flags are parsed in a case-insensitive manner.
        Defaults to ``False``.
    prefix: :class:`str`
        The prefix that all flags must be prefixed with. By default,
        there is no prefix.
    delimiter: :class:`str`
        The delimiter that separates a flag's argument from the flag's name.
        By default, this is ``:``.
    """

    @classmethod
    def get_flags(cls) -> dict[str, Flag]:
        """A mapping of flag name to flag object this converter has."""
        return cls.__commands_flags__.copy()

    @classmethod
    def _can_be_constructible(cls) -> bool:
        return all(not flag.required for flag in cls.__commands_flags__.values())

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        for flag in self.__class__.__commands_flags__.values():
            yield flag.name, getattr(self, flag.attribute)

    @classmethod
    async def _construct_default(cls: type[F], ctx: "Context") -> F:
        self: F = cls.__new__(cls)
        flags = cls.__commands_flags__
        for flag in flags.values():
            if callable(flag.default):
                default = await maybe_coroutine(flag.default, ctx)
                setattr(self, flag.attribute, default)
            else:
                setattr(self, flag.attribute, flag.default)
        return self

    def __repr__(self) -> str:
        pairs = " ".join(
            [
                f"{flag.attribute}={getattr(self, flag.attribute)!r}"
                for flag in self.get_flags().values()
            ]
        )
        return f"<{self.__class__.__name__} {pairs}>"

    @classmethod
    def parse_flags(cls, argument: str) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        flags = cls.__commands_flags__
        aliases = cls.__commands_flag_aliases__
        last_position = 0
        last_flag: Flag | None = None

        case_insensitive = cls.__commands_flag_case_insensitive__
        for match in cls.__commands_flag_regex__.finditer(argument):
            begin, end = match.span(0)
            key = match.group("flag")
            if case_insensitive:
                key = key.casefold()

            if key in aliases:
                key = aliases[key]

            flag = flags.get(key)
            if last_position and last_flag is not None:
                value = argument[last_position : begin - 1].lstrip()
                if not value:
                    raise MissingFlagArgument(last_flag)

                try:
                    values = result[last_flag.name]
                except KeyError:
                    result[last_flag.name] = [value]
                else:
                    values.append(value)

            last_position = end
            last_flag = flag

        # Add the remaining string to the last available flag
        if last_position and last_flag is not None:
            value = argument[last_position:].strip()
            if not value:
                raise MissingFlagArgument(last_flag)

            try:
                values = result[last_flag.name]
            except KeyError:
                result[last_flag.name] = [value]
            else:
                values.append(value)

        # Verification of values will come at a later stage
        return result

    @classmethod
    async def convert(cls: type[F], ctx: "Context", argument: str) -> F:
        """|coro|

        The method that actually converters an argument to the flag mapping.

        Parameters
        ----------
        cls: Type[:class:`FlagConverter`]
            The flag converter class.
        ctx: :class:`Context`
            The invocation context.
        argument: :class:`str`
            The argument to convert from.

        Returns
        -------
        :class:`FlagConverter`
            The flag converter instance with all flags parsed.

        Raises
        ------
        FlagError
            A flag related parsing error.
        CommandError
            A command related error.
        """
        arguments = cls.parse_flags(argument)
        flags = cls.__commands_flags__

        self: F = cls.__new__(cls)
        for name, flg in flags.items():
            try:
                values = arguments[name]
            except KeyError:
                if flg.required:
                    raise MissingRequiredFlag(flg)
                else:
                    if callable(flg.default):
                        default = await maybe_coroutine(flg.default, ctx)
                        setattr(self, flg.attribute, default)
                    else:
                        setattr(self, flg.attribute, flg.default)
                    continue

            if 0 < flg.max_args < len(values):  # type: ignore[operator]
                if flg.override:  # type: ignore[truthy-function]
                    values = values[-flg.max_args :]  # type: ignore[index]
                else:
                    raise TooManyFlags(flg, values)

            # Special case:
            if flg.max_args == 1:  # type: ignore[comparison-overlap]
                value = await convert_flag(ctx, values[0], flg)
                setattr(self, flg.attribute, value)
                continue

            # Another special case, tuple parsing.
            # Tuple parsing is basically converting arguments within the flag
            # So, given flag: hello 20 as the input and Tuple[str, int] as the type hint
            # We would receive ('hello', 20) as the resulting value
            # This uses the same whitespace and quoting rules as regular parameters.
            values = [await convert_flag(ctx, value, flg) for value in values]

            if flg.cast_to_dict:
                values = dict(values)  # type: ignore

            setattr(self, flg.attribute, values)

        return self
