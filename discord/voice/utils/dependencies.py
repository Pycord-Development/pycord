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

import logging

try:
    import davey
except ImportError:
    HAS_DAVEY = False
    DAVE_PROTOCOL_VERSION = 0
else:
    HAS_DAVEY = True
    DAVE_PROTOCOL_VERSION = davey.DAVE_PROTOCOL_VERSION

try:
    import nacl.secret
    import nacl.utils
except ImportError:
    HAS_NACL = False
else:
    HAS_NACL = True

VOICE_DEPENDENCY_WARNING_EMITTED = False

_log = logging.getLogger("discord.client")


def get_missing_voice_dependencies() -> tuple[str, ...]:
    missing: list[str] = []
    if not HAS_NACL:
        missing.append("PyNaCl")
    if not HAS_DAVEY:
        missing.append("davey")
    return tuple(missing)


def warn_if_voice_dependencies_missing() -> None:
    global VOICE_DEPENDENCY_WARNING_EMITTED
    if VOICE_DEPENDENCY_WARNING_EMITTED:
        return

    missing = get_missing_voice_dependencies()
    if not missing:
        return

    VOICE_DEPENDENCY_WARNING_EMITTED = True
    deps = ", ".join(missing)
    _log.warning(
        "%s %s not installed, voice will NOT be supported",
        deps,
        "is" if len(missing) == 1 else "are",
    )
