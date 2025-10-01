from __future__ import annotations

import array
import asyncio
import collections.abc
import datetime
import functools
import re
import sys
import types
import unicodedata
import warnings
from _bisect import bisect_left
from base64 import b64encode
from inspect import isawaitable, signature
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Coroutine,
    ForwardRef,
    Generic,
    Iterable,
    Iterator,
    Literal,
    ParamSpec,
    Sequence,
    TypeVar,
    Union,
    get_args,
    overload,
)

from ..errors import HTTPException, InvalidArgument

if TYPE_CHECKING:
    from ..invite import Invite
    from ..template import Template

_IS_ASCII = re.compile(r"^[\x00-\x7f]+$")

P = ParamSpec("P")
T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


def resolve_invite(invite: Invite | str) -> str:
    """
    Resolves an invite from a :class:`~discord.Invite`, URL or code.

    Parameters
    ----------
    invite: Union[:class:`~discord.Invite`, :class:`str`]
        The invite.

    Returns
    -------
    :class:`str`
        The invite code.
    """
    from ..invite import Invite  # noqa: PLC0415 # circular import

    if isinstance(invite, Invite):
        return invite.code
    rx = r"(?:https?\:\/\/)?discord(?:\.gg|(?:app)?\.com\/invite)\/(.+)"
    m = re.match(rx, invite)
    if m:
        return m.group(1)
    return invite


def get_as_snowflake(data: Any, key: str) -> int | None:
    try:
        value = data[key]
    except KeyError:
        return None
    else:
        return value and int(value)


def get_mime_type_for_image(data: bytes):
    if data.startswith(b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"):
        return "image/png"
    elif data[0:3] == b"\xff\xd8\xff" or data[6:10] in (b"JFIF", b"Exif"):
        return "image/jpeg"
    elif data.startswith((b"\x47\x49\x46\x38\x37\x61", b"\x47\x49\x46\x38\x39\x61")):
        return "image/gif"
    elif data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    else:
        raise InvalidArgument("Unsupported image type given")


def bytes_to_base64_data(data: bytes) -> str:
    fmt = "data:{mime};base64,{data}"
    mime = get_mime_type_for_image(data)
    b64 = b64encode(data).decode("ascii")
    return fmt.format(mime=mime, data=b64)


def parse_ratelimit_header(request: Any, *, use_clock: bool = False) -> float:
    reset_after: str | None = request.headers.get("X-Ratelimit-Reset-After")
    if not use_clock and reset_after:
        return float(reset_after)
    utc = datetime.timezone.utc
    now = datetime.datetime.now(utc)
    reset = datetime.datetime.fromtimestamp(float(request.headers["X-Ratelimit-Reset"]), utc)
    return (reset - now).total_seconds()


def string_width(string: str, *, _IS_ASCII: re.Pattern[str] = _IS_ASCII) -> int:
    """Returns string's width."""
    match = _IS_ASCII.match(string)
    if match:
        return match.endpos

    UNICODE_WIDE_CHAR_TYPE = "WFA"
    func = unicodedata.east_asian_width
    return sum(2 if func(char) in UNICODE_WIDE_CHAR_TYPE else 1 for char in string)


def resolve_template(code: Template | str) -> str:
    """
    Resolves a template code from a :class:`~discord.Template`, URL or code.

    .. versionadded:: 1.4

    Parameters
    ----------
    code: Union[:class:`~discord.Template`, :class:`str`]
        The code.

    Returns
    -------
    :class:`str`
        The template code.
    """
    from ..template import Template  # noqa: PLC0415

    if isinstance(code, Template):
        return code.code
    rx = r"(?:https?\:\/\/)?discord(?:\.new|(?:app)?\.com\/template)\/(.+)"
    m = re.match(rx, code)
    if m:
        return m.group(1)
    return code


__all__ = (
    "resolve_invite",
    "get_as_snowflake",
    "get_mime_type_for_image",
    "bytes_to_base64_data",
    "parse_ratelimit_header",
    "string_width",
)


@overload
def parse_time(timestamp: None) -> None: ...


@overload
def parse_time(timestamp: str) -> datetime.datetime: ...


def parse_time(timestamp: str | None) -> datetime.datetime | None:
    """A helper function to convert an ISO 8601 timestamp to a datetime object.

    Parameters
    ----------
    timestamp: Optional[:class:`str`]
        The timestamp to convert.

    Returns
    -------
    Optional[:class:`datetime.datetime`]
        The converted datetime object.
    """
    if timestamp:
        return datetime.datetime.fromisoformat(timestamp)
    return None


def warn_deprecated(
    name: str,
    instead: str | None = None,
    since: str | None = None,
    removed: str | None = None,
    reference: str | None = None,
    stacklevel: int = 3,
) -> None:
    """Warn about a deprecated function, with the ability to specify details about the deprecation. Emits a
    DeprecationWarning.

    Parameters
    ----------
    name: str
        The name of the deprecated function.
    instead: Optional[:class:`str`]
        A recommended alternative to the function.
    since: Optional[:class:`str`]
        The version in which the function was deprecated. This should be in the format ``major.minor(.patch)``, where
        the patch version is optional.
    removed: Optional[:class:`str`]
        The version in which the function is planned to be removed. This should be in the format
        ``major.minor(.patch)``, where the patch version is optional.
    reference: Optional[:class:`str`]
        A reference that explains the deprecation, typically a URL to a page such as a changelog entry or a GitHub
        issue/PR.
    stacklevel: :class:`int`
        The stacklevel kwarg passed to :func:`warnings.warn`. Defaults to 3.
    """
    message = f"{name} is deprecated"
    if since:
        message += f" since version {since}"
    if removed:
        message += f" and will be removed in version {removed}"
    if instead:
        message += f", consider using {instead} instead"
    message += "."
    if reference:
        message += f" See {reference} for more information."

    warnings.warn(message, stacklevel=stacklevel, category=DeprecationWarning)


def deprecated(
    instead: str | None = None,
    since: str | None = None,
    removed: str | None = None,
    reference: str | None = None,
    stacklevel: int = 3,
    *,
    use_qualname: bool = True,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """A decorator implementation of :func:`warn_deprecated`. This will automatically call :func:`warn_deprecated` when
    the decorated function is called.

    Parameters
    ----------
    instead: Optional[:class:`str`]
        A recommended alternative to the function.
    since: Optional[:class:`str`]
        The version in which the function was deprecated. This should be in the format ``major.minor(.patch)``, where
        the patch version is optional.
    removed: Optional[:class:`str`]
        The version in which the function is planned to be removed. This should be in the format
        ``major.minor(.patch)``, where the patch version is optional.
    reference: Optional[:class:`str`]
        A reference that explains the deprecation, typically a URL to a page such as a changelog entry or a GitHub
        issue/PR.
    stacklevel: :class:`int`
        The stacklevel kwarg passed to :func:`warnings.warn`. Defaults to 3.
    use_qualname: :class:`bool`
        Whether to use the qualified name of the function in the deprecation warning. If ``False``, the short name of
        the function will be used instead. For example, __qualname__ will display as ``Client.login`` while __name__
        will display as ``login``. Defaults to ``True``.
    """

    def actual_decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def decorated(*args: P.args, **kwargs: P.kwargs) -> T:
            warn_deprecated(
                name=func.__qualname__ if use_qualname else func.__name__,
                instead=instead,
                since=since,
                removed=removed,
                reference=reference,
                stacklevel=stacklevel,
            )
            return func(*args, **kwargs)

        return decorated

    return actual_decorator


PY_310 = sys.version_info >= (3, 10)


def flatten_literal_params(parameters: Iterable[Any]) -> tuple[Any, ...]:
    params: list[Any] = []
    literal_cls = type(Literal[0])
    for p in parameters:
        if isinstance(p, literal_cls):
            params.extend(get_args(p))
        else:
            params.append(p)
    return tuple(params)


def normalise_optional_params(parameters: Iterable[Any]) -> tuple[Any, ...]:
    none_cls = type(None)
    return tuple(p for p in parameters if p is not none_cls) + (none_cls,)


def evaluate_annotation(
    tp: Any,
    globals: dict[str, Any],
    locals: dict[str, Any],
    cache: dict[str, Any],
    *,
    implicit_str: bool = True,
) -> Any:
    if isinstance(tp, ForwardRef):
        tp = tp.__forward_arg__
        # ForwardRefs always evaluate their internals
        implicit_str = True

    if implicit_str and isinstance(tp, str):
        if tp in cache:
            return cache[tp]
        evaluated = eval(tp, globals, locals)
        cache[tp] = evaluated
        return evaluate_annotation(evaluated, globals, locals, cache)

    if hasattr(tp, "__args__"):
        implicit_str = True
        is_literal = False
        args = tp.__args__
        if not hasattr(tp, "__origin__"):
            if PY_310 and tp.__class__ is types.UnionType:
                converted = Union[args]  # noqa: UP007
                return evaluate_annotation(converted, globals, locals, cache)

            return tp
        if tp.__origin__ is Union:
            try:
                if args.index(type(None)) != len(args) - 1:
                    args = normalise_optional_params(tp.__args__)
            except ValueError:
                pass
        if tp.__origin__ is Literal:
            if not PY_310:
                args = flatten_literal_params(tp.__args__)
            implicit_str = False
            is_literal = True

        evaluated_args = tuple(
            evaluate_annotation(arg, globals, locals, cache, implicit_str=implicit_str) for arg in args
        )

        if is_literal and not all(isinstance(x, (str, int, bool, type(None))) for x in evaluated_args):
            raise TypeError("Literal arguments must be of type str, int, bool, or NoneType.")

        if evaluated_args == args:
            return tp

        try:
            return tp.copy_with(evaluated_args)
        except AttributeError:
            return tp.__origin__[evaluated_args]

    return tp


def resolve_annotation(
    annotation: Any,
    globalns: dict[str, Any],
    localns: dict[str, Any] | None,
    cache: dict[str, Any] | None,
) -> Any:
    if annotation is None:
        return type(None)
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)

    locals = globalns if localns is None else localns
    if cache is None:
        cache = {}
    return evaluate_annotation(annotation, globalns, locals, cache)


def delay_task(delay: float, func: Coroutine[Any, Any, Any]):
    async def inner_call():
        await asyncio.sleep(delay)
        try:
            await func
        except HTTPException:
            pass

    asyncio.create_task(inner_call())


async def async_all(gen: Iterable[Any]) -> bool:
    for elem in gen:
        if isawaitable(elem):
            elem = await elem
        if not elem:
            return False
    return True


async def maybe_awaitable(f: Callable[P, T | Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> T:
    value = f(*args, **kwargs)
    if isawaitable(value):
        return await value
    return value


async def sane_wait_for(futures: Iterable[Awaitable[T]], *, timeout: float) -> set[asyncio.Task[T]]:
    ensured = [asyncio.ensure_future(fut) for fut in futures]
    done, pending = await asyncio.wait(ensured, timeout=timeout, return_when=asyncio.ALL_COMPLETED)

    if len(pending) != 0:
        raise asyncio.TimeoutError()

    return done


class SnowflakeList(array.array[int]):
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
        return super().__new__(cls, "Q", data if is_sorted else sorted(data))

    def add(self, element: int) -> None:
        i = bisect_left(self, element)
        self.insert(i, element)

    def get(self, element: int) -> int | None:
        i = bisect_left(self, element)
        return self[i] if i != len(self) and self[i] == element else None

    def has(self, element: int) -> bool:
        i = bisect_left(self, element)
        return i != len(self) and self[i] == element


def copy_doc(original: Callable[..., object]) -> Callable[[T], T]:
    def decorator(overridden: T) -> T:
        overridden.__doc__ = original.__doc__
        overridden.__signature__ = signature(original)  # type: ignore[reportAttributeAccessIssue]
        return overridden

    return decorator


class SequenceProxy(collections.abc.Sequence[T_co], Generic[T_co]):
    """Read-only proxy of a Sequence."""

    def __init__(self, proxied: Sequence[T_co]):
        self.__proxied = proxied

    @overload
    def __getitem__(self, idx: int) -> T_co: ...
    @overload
    def __getitem__(self, idx: slice) -> Sequence[T_co]: ...

    def __getitem__(self, idx: int | slice) -> T_co | Sequence[T_co]:
        return self.__proxied[idx]

    def __len__(self) -> int:
        return len(self.__proxied)

    def __contains__(self, item: Any) -> bool:
        return item in self.__proxied

    def __iter__(self) -> Iterator[T_co]:
        return iter(self.__proxied)

    def __reversed__(self) -> Iterator[T_co]:
        return reversed(self.__proxied)

    def index(self, value: Any, *args: Any, **kwargs: Any) -> int:
        return self.__proxied.index(value, *args, **kwargs)

    def count(self, value: Any) -> int:
        return self.__proxied.count(value)


class CachedSlotProperty(Generic[T, T_co]):
    def __init__(self, name: str, function: Callable[[T], T_co]) -> None:
        self.name = name
        self.function = function
        self.__doc__ = function.__doc__

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


def get_slots(cls: type[Any]) -> Iterator[str]:
    for mro in reversed(cls.__mro__):
        slots = getattr(mro, "__slots__", None)
        if slots is None:
            continue
        yield from slots


def cached_slot_property(
    name: str,
) -> Callable[[Callable[[T], T_co]], CachedSlotProperty[T, T_co]]:
    def decorator(func: Callable[[T], T_co]) -> CachedSlotProperty[T, T_co]:
        return CachedSlotProperty(name, func)

    return decorator


try:
    import msgspec

    def to_json(obj: Any) -> str:  # type: ignore[reportUnusedFunction]
        return msgspec.json.encode(obj).decode("utf-8")

    from_json = msgspec.json.decode

except ModuleNotFoundError:
    import json

    def to_json(obj: Any) -> str:  # type: ignore[reportUnusedFunction]
        return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)

    from_json = json.loads
