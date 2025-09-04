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

import datetime
import re
import warnings

from typing_extensions import TypedDict

__all__ = ("__version__", "VersionInfo", "version_info")

from typing import Literal, NamedTuple

from .utils.private import deprecated
from ._version import __version__, __version_tuple__


class AdvancedVersionInfo(TypedDict):
    serial: int
    build: int | None
    commit: str | None
    date: datetime.date | None


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final", "dev"]

    # We can't set instance attributes on a NamedTuple, so we have to use a
    # global variable to store the advanced version info.
    @property
    def advanced(self) -> AdvancedVersionInfo:
        return _advanced

    @advanced.setter
    def advanced(self, value: object) -> None:
        global _advanced
        _advanced = value

    @property
    @deprecated("releaselevel", "2.4")
    def release_level(self) -> Literal["alpha", "beta", "candidate", "final", "dev"]:
        return self.releaselevel

    @property
    @deprecated('.advanced["serial"]', "2.4")
    def serial(self) -> int:
        return self.advanced["serial"]

    @property
    @deprecated('.advanced["build"]', "2.4")
    def build(self) -> int | None:
        return self.advanced["build"]

    @property
    @deprecated('.advanced["commit"]', "2.4")
    def commit(self) -> str | None:
        return self.advanced["commit"]

    @property
    @deprecated('.advanced["date"]', "2.4")
    def date(self) -> datetime.date | None:
        return self.advanced["date"]


def parse_version_tuple(version_tuple):
    """Parse setuptools-scm version tuple into components."""
    major = version_tuple[0] if len(version_tuple) > 0 else 0
    minor = version_tuple[1] if len(version_tuple) > 1 else 0
    micro = 0
    releaselevel = "final"
    serial = 0
    build = None
    commit = None
    date_info = None

    # Handle additional components
    for i, component in enumerate(version_tuple[2:], start=2):
        if isinstance(component, str):
            # Parse development/pre-release info
            if component.startswith("dev"):
                releaselevel = "dev"  # Keep dev as its own category
                serial = int(component[3:]) if len(component) > 3 else 0
            elif component.startswith("a"):
                releaselevel = "alpha"
                serial = int(component[1:]) if len(component) > 1 else 0
            elif component.startswith("b"):
                releaselevel = "beta"
                serial = int(component[1:]) if len(component) > 1 else 0
            elif component.startswith("rc"):
                releaselevel = "candidate"
                serial = int(component[2:]) if len(component) > 2 else 0
            elif component.startswith("g") and "." in component:
                # Parse git info like 'g901fb98.d20250526'
                parts = component.split(".")
                if parts[0].startswith("g"):
                    commit = parts[0][1:]  # Remove 'g' prefix
                if len(parts) > 1 and parts[1].startswith("d"):
                    date_str = parts[1][1:]  # Remove 'd' prefix
                    if len(date_str) == 8:
                        date_info = datetime.date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]))
        elif isinstance(component, int) and i == 2:
            micro = component

    return {
        "major": major,
        "minor": minor,
        "micro": micro,
        "releaselevel": releaselevel,
        "serial": serial,
        "build": build,
        "commit": commit,
        "date": date_info,
    }


# Parse the version tuple
parsed = parse_version_tuple(__version_tuple__)

version_info: VersionInfo = VersionInfo(
    major=parsed["major"],
    minor=parsed["minor"],
    micro=parsed["micro"],
    releaselevel=parsed["releaselevel"],
)

_advanced = AdvancedVersionInfo(
    serial=parsed["serial"],
    build=parsed["build"],
    commit=parsed["commit"],
    date=parsed["date"],
)
