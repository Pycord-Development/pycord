from __future__ import annotations

import datetime
import functools
import re
import sys
import types
import unicodedata
import warnings
from base64 import b64encode
from typing import TYPE_CHECKING, Any, overload, Callable, TypeVar, ParamSpec, Iterable, Literal, ForwardRef, Union

from ..errors import InvalidArgument

if TYPE_CHECKING:
    from ..invite import Invite
    from ..template import Template

_IS_ASCII = re.compile(r"^[\x00-\x7f]+$")


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
    from ..invite import Invite  # circular import

    if isinstance(invite, Invite):
        return invite.code
    rx = r"(?:https?\:\/\/)?discord(?:\.gg|(?:app)?\.com\/invite)\/(.+)"
    m = re.match(rx, invite)
    if m:
        return m.group(1)
    return invite


__all__ = ("resolve_invite",)


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


def string_width(string: str, *, _IS_ASCII=_IS_ASCII) -> int:
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
    from .template import Template  # circular import

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


@overload
def parse_time(timestamp: str | None) -> datetime.datetime | None: ...


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
    warnings.simplefilter("always", DeprecationWarning)  # turn off filter
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
    warnings.simplefilter("default", DeprecationWarning)  # reset filter


P = ParamSpec("P")
T = TypeVar("T")


def deprecated(
    instead: str | None = None,
    since: str | None = None,
    removed: str | None = None,
    reference: str | None = None,
    stacklevel: int = 3,
    *,
    use_qualname: bool = True,
) -> Callable[[Callable[[P], T]], Callable[[P], T]]:
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

    def actual_decorator(func: Callable[[P], T]) -> Callable[[P], T]:
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
    params = []
    literal_cls = type(Literal[0])
    for p in parameters:
        if isinstance(p, literal_cls):
            params.extend(p.__args__)
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
):
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
            if PY_310 and tp.__class__ is types.UnionType:  # type: ignore
                converted = Union[args]  # type: ignore
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
