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

from .public import (
    MISSING,
    UNICODE_EMOJIS,
    Undefined,
    basic_autocomplete,
    escape_markdown,
    escape_mentions,
    find,
    format_dt,
    generate_snowflake,
    oauth_url,
    raw_channel_mentions,
    raw_mentions,
    raw_role_mentions,
    remove_markdown,
    snowflake_time,
    utcnow,
)

DISCORD_EPOCH = 1420070400000


__all__ = (
    "oauth_url",
    "snowflake_time",
    "find",
    "utcnow",
    "remove_markdown",
    "escape_markdown",
    "escape_mentions",
    "raw_mentions",
    "raw_channel_mentions",
    "raw_role_mentions",
    "format_dt",
    "generate_snowflake",
    "basic_autocomplete",
    "Undefined",
    "MISSING",
    "UNICODE_EMOJIS",
)
