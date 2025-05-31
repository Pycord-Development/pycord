from __future__ import annotations

import datetime
import re
import unicodedata
from base64 import b64encode
from typing import TYPE_CHECKING, Any

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
    reset = datetime.datetime.fromtimestamp(
        float(request.headers["X-Ratelimit-Reset"]), utc
    )
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

