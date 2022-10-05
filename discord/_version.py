import re
import warnings
from datetime import date
from importlib.metadata import PackageNotFoundError, version

__all__ = ("__version__", "VersionInfo", "version_info")

from typing import Literal, NamedTuple, Optional

from discord.utils import deprecated

try:
    __version__ = version("py-cord")
    print("Set version")
except PackageNotFoundError:
    # Package is not installed
    try:
        from setuptools_scm import get_version  # type: ignore[import]

        __version__ = get_version()
        print("set version")
    except ImportError:
        # setuptools_scm is not installed
        __version__ = "0.0.0"
        warnings.warn(
            "Package is not installed, and setuptools_scm is not installed. "
            f"As a fallback, {__name__}.__version__ will be set to {__version__}",
            RuntimeWarning,
            stacklevel=2,
        )


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    release_level: Literal["alpha", "beta", "candidate", "final"]
    serial: int
    build: int | None = None
    commit: str | None = None
    date: Optional[date] = None

    @property
    @deprecated("release_level", "2.3")
    def releaselevel(self) -> Literal["alpha", "beta", "candidate", "final"]:
        return self.release_level


version_regex = re.compile(
    r"^(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?"
    r"(?:(?P<level>rc|a|b)(?P<serial>\d+))?"
    r"(?:\.dev(?P<build>\d+))?"
    r"(?:\+(?:(?:g(?P<commit>[a-fA-F0-9]{8})\.d(?P<date>\d{4}\d{2}\d{2}))|d(?P<date1>\d{4}\d{2}\d{2})))?$"
)

raw_info = version_regex.match(__version__).groupdict()

level_info: Literal["alpha", "beta", "candidate", "final"]

if raw_info["level"] == "a":
    level_info = "alpha"
elif raw_info["level"] == "b":
    level_info = "beta"
elif raw_info["level"] == "rc":
    level_info = "candidate"
elif raw_info["level"] is None:
    level_info = "final"
else:
    raise RuntimeError("Invalid release level")

if (raw_date := raw_info["date"] or raw_info["date1"]) is not None:
    date_info = date(
        int(raw_date[:4]),
        int(raw_date[4:6]),
        int(raw_date[6:]),
    )
else:
    date_info = None

version_info: VersionInfo = VersionInfo(
    major=raw_info["major"],
    minor=raw_info["minor"],
    micro=raw_info["patch"],
    release_level=level_info,
    serial=raw_info["serial"],
    build=raw_info["build"],
    commit=raw_info["commit"],
    date=date_info,
)
