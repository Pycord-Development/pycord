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

from typing import TYPE_CHECKING, Literal, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .collectibles import AvatarDecoration, Collectibles
    from .primary_guild import PrimaryGuild
    from .snowflake import Snowflake


class PartialUser(TypedDict):
    id: Snowflake
    username: str
    discriminator: str
    global_name: str | None
    avatar: str | None


PremiumType = Literal[0, 1, 2, 3]


class User(PartialUser):
    bot: NotRequired[bool]
    system: NotRequired[bool]
    mfa_enabled: NotRequired[bool]
    banner: NotRequired[str | None]
    accent_color: NotRequired[int | None]
    locale: NotRequired[str]
    verified: NotRequired[bool]
    email: NotRequired[str | None]
    flags: NotRequired[int]
    premium_type: NotRequired[PremiumType]
    public_flags: NotRequired[int]
    avatar_decoration_data: NotRequired[AvatarDecoration | None]
    collectibles: NotRequired[Collectibles | None]
    primary_guild: NotRequired[PrimaryGuild | None]
