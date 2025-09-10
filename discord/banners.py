from __future__ import annotations

import datetime
import importlib.resources
import logging
import logging.config
import os
import platform
import string
import sys
import time
import warnings
from typing import Sequence

import colorlog
import colorlog.escape_codes

from . import __version__

__all__: Sequence[str] = ("start_logging", "print_banner")


day_prefixes: dict[int, str] = {
    1: "st",
    2: "nd",
    3: "rd",
    4: "th",
    5: "th",
    6: "th",
    7: "th",
    8: "th",
    9: "th",
    0: "th",
}


def start_logging(flavor: None | int | str | dict, debug: bool = False):
    if len(logging.root.handlers) != 0:
        return  # the user is most likely using logging.basicConfig, or is being spearheaded by something else.

    if flavor is None:
        flavor = logging.DEBUG if debug else logging.INFO

    if isinstance(flavor, dict):
        logging.config.dictConfig(flavor)

        if flavor.get("handler"):
            return

        flavor = None

    # things that will never be logged.
    logging.logThreads = None
    logging.logProcesses = None

    colorlog.basicConfig(
        level=flavor,
        format="%(log_color)s%(bold)s%(levelname)-1.1s%(thin)s %(asctime)23.23s %(bold)s%(name)s: "
        "%(thin)s%(message)s%(reset)s",
        stream=sys.stderr,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red, bg_white",
        },
    )
    warnings.simplefilter("always", DeprecationWarning)
    logging.captureWarnings(True)


def get_day_prefix(num: int) -> str:
    n = str(num)
    return day_prefixes[int(n[len(n) - 1])]


def print_banner(
    bot_name: str = "A bot",
    module: str | None = "pycord",
):
    banners = importlib.resources.files(module)

    for trav in banners.iterdir():
        if trav.name == "banner.txt":
            banner = trav.read_text()
        elif trav.name == "ibanner.txt":
            info_banner = trav.read_text()

    today = datetime.datetime.now().date()

    args = {
        # the # prefix only works on Windows, and the - prefix only works on linux/unix systems
        "current_time": today.strftime(f"%B the %#d{get_day_prefix(today.day)} of %Y")
        if os.name == "nt"
        else today.strftime(f"%B the %-d{get_day_prefix(today.day)} of %Y"),
        "py_version": platform.python_version(),
        "botname": bot_name,
        "version": __version__,
    }
    args |= colorlog.escape_codes.escape_codes

    sys.stdout.write(string.Template(banner).safe_substitute(args))
    sys.stdout.write(string.Template(info_banner).safe_substitute(args))
    sys.stdout.flush()
    time.sleep(0.162)  # sleep for a bit to prevent overfill.
