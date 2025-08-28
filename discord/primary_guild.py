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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import ConnectionState

from .asset import Asset
from .types.primary_guild import PrimaryGuild as PrimaryGuildPayload

__all__ = ("PrimaryGuild",)


class PrimaryGuild:
    """
    Represents a Discord Primary Guild.

    .. versionadded:: 2.7

    Attributes
    ----------
    identity_guild_id: int
        The ID of the guild.
    identity_enabled: :class:`bool`
        Whether the primary guild is enabled.
    tag: str
        The tag of the primary guild.
    """

    def __init__(self, data: PrimaryGuildPayload, state: "ConnectionState") -> None:
        self.identity_guild_id: int | None = (
            int(data.get("identity_guild_id", 0)) or None
        )
        self.identity_enabled: bool | None = data.get("identity_enabled", None)
        self.tag: str | None = data.get("tag", None)
        self._badge: str | None = data.get("badge", None)
        self._state: "ConnectionState" = state

    def __repr__(self) -> str:
        return f"<PrimaryGuild identity_guild_id={self.identity_guild_id} identity_enabled={self.identity_enabled} tag={self.tag}>"

    @property
    def badge(self) -> Asset | None:
        """Returns the badge asset, if available.

        .. versionadded:: 2.7
        """
        if self._badge is None:
            return None
        return Asset._from_user_primary_guild_tag(
            self._state, self.identity_guild_id, self._badge
        )
