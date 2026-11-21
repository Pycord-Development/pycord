"""
The MIT License (MIT)

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

from typing import TYPE_CHECKING, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .snowflake import Snowflake
    from .user import User


class SoundboardSound(TypedDict):
    name: str
    sound_id: Snowflake
    volume: float
    emoji_id: Snowflake | None
    emoji_name: str | None
    guild_id: NotRequired[Snowflake]
    available: bool
    user: NotRequired[User]


class CreateSoundboardSound(TypedDict):
    """Allowed fields when creating a soundboard sound"""

    name: str
    sound: str
    volume: NotRequired[float | None]
    emoji_id: NotRequired[Snowflake | None]
    emoji_name: NotRequired[str | None]


class ModifySoundboardSound(TypedDict):
    """Allowed fields when modifying a soundboard sound"""

    name: NotRequired[str]
    volume: NotRequired[float | None]
    emoji_id: NotRequired[Snowflake | None]
    emoji_name: NotRequired[str | None]
