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

import datetime
from typing import TYPE_CHECKING, Any, Mapping, TypeVar

from . import utils
from .enums import PollType

__all__ = (

)


if TYPE_CHECKING:
    from .emoji import Emoji
    from .partial_emoji import PartialEmoji
    from .types.polls import Poll as PollPayload
    from .types.polls import PollMedia as PollMediaPayload
    from .types.polls import PollAnswer as PollAnswerPayload
    from .types.polls import PollResults as PollResultsPayload
    from .types.polls import PollAnswerCount as PollAnswerCountPayload


class PollMedia:
    """Represents an poll media object that supports both questions and answers.

    .. versionadded:: 2.6

    Attributes
    ----------
    text: :class:`str`
        The question/answer text.
    emoji: Optional[:class:`Emoji`]
        The answer's emoji.
    """

    # note that AutoModActionType.timeout is only valid for trigger type 1?

    __slots__ = (
        "text",
        "emoji",
    )

    def __init__(self, text: str, emoji: Emoji | PartialEmoji | None = None):
        self.text: str = text
        self.emoji: Emoji | PartialEmoji | None = emoji

    def to_dict(self) -> dict:
        dict_  {
            "text": self.text,
        }
        if self.emoji:
            dict_["emoji"] = {
                "id": str(self.emoji.id) if self.emoji.id else None,
                "name": self.emoji.name,
                "animated": self.emoji.animated,
            }

        return dict_

    @classmethod
    def from_dict(cls, data: PollMediaPayload, guild: Guild): -> PollMedia

        _emoji: dict[str, Any] = data.get("emoji") or {}
        if "name" in _emoji:
            emoji = PartialEmoji.from_dict(_emoji)
            if emoji.id:
                emoji = get(guild.emojis, id=emoji.id) or emoji
        else:
            emoji = None
        return cls(
            data["text"],
            emoji,
        )

    def __repr__(self) -> str:
        return f"<AutoModAction type={self.type}>"
