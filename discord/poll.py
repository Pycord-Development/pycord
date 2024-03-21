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
from typing import TYPE_CHECKING, Any

from . import utils
from .enums import PollLayoutType
from .iterators import AsyncIterator

__all__ = ()


if TYPE_CHECKING:
    from .emoji import Emoji
    from .partial_emoji import PartialEmoji
    from .types.poll import Poll as PollPayload
    from .types.poll import PollAnswer as PollAnswerPayload
    from .types.poll import PollAnswerCount as PollAnswerCountPayload
    from .types.poll import PollMedia as PollMediaPayload
    from .types.poll import PollResults as PollResultsPayload
    from .user import User


class PollMedia:
    """Represents a poll media object that supports both questions and answers.

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

    def to_dict(self) -> PollMediaPayload:
        dict_ = {
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
    def from_dict(cls, data: PollMediaPayload, guild: Guild) -> PollMedia:

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
        return f"<PollMedia text={self.text!r} emoji={self.emoji!r}>"


class PollAnswer:
    """Represents a poll answer object.

    .. versionadded:: 2.6

    Attributes
    ----------
    id: :class:`int`
        The answer's ID. It currently starts at ``1`` for the first answer, then goes up sequentially.
        It may not be reliable to depend on this.
    text: :class:`str`
        The answer's text.
    emoji: Optional[:class:`Emoji`]
        The answer's emoji.
    """

    __slots__ = (
        "_media",
        "id",
        "text",
        "emoji",
    )

    def __init__(self, id: int, media: PollMedia):
        self.id = id
        self._media = media
        self.text: str = media.text
        self.emoji: Emoji | PartialEmoji | None = media.emoji

    def to_dict(self) -> PollAnswerPayload:
        return {
            "id": self.id,
            "poll_media": self._media.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: PollAnswerPayload) -> PollAnswer:
        return cls(
            data["answer_id"],
            PollMedia.from_dict(data["poll_media"]),
        )

    def __repr__(self) -> str:
        return f"<Pollmedia text={self.text!r} emoji={self.emoji!r}>"

    def users(
        self, *, limit: int | None = None, after: Snowflake | None = None
    ) -> AsyncIterator:
        """Returns an :class:`AsyncIterator` representing the users that have voted with this answer.

        The ``after`` parameter must represent a member
        and meet the :class:`abc.Snowflake` abc.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The maximum number of results to return.
            If not provided, returns all the users who
            voted with this answer.
        after: Optional[:class:`abc.Snowflake`]
            For pagination, reactions are sorted by member.

        Yields
        ------
        Union[:class:`User`, :class:`Member`]
            The member (if retrievable) or the user that has voted
            with this answer. The case where it can be a :class:`Member` is
            in a guild message context. Sometimes it can be a :class:`User`
            if the member has left the guild.

        Raises
        ------
        HTTPException
            Getting the voters for the answer failed.

        Examples
        --------

        Usage ::

            async for user in answer.users():
                print(f'{user} voted **{answer.text}**!')

        Flattening into a list: ::

            users = await answer.users().flatten()
            # users is now a list of User...
            winner = random.choice(users)
            await channel.send(f'{winner} has won the raffle.')
        """

        if limit is None:
            limit = self.count

        return AsyncIterator(...)  # TODO


class PollAnswerCount:
    """Represents a poll answer count object.

    .. versionadded:: 2.6

    Attributes
    ----------
    id: :class:`int`
        The answer's ID. It currently starts at ``1`` for the first answer, then goes up sequentially.
        It may not be reliable to depend on this.
    count: :class:`int`
        The number of votes for this answer.
    me: :class:`bool`
        If the current user voted this answer. This is always ``False`` for bots.
    """

    __slots__ = (
        "id",
        "count",
        "me",
    )

    def __init__(self, data: PollAnswerCountPayload):
        self.id = data["id"]
        self.count: int = data.get("count", 0)
        self.me = data.get("me_voted")

    def to_dict(self) -> PollAnswerPayload:
        return {"answer_id": self.id, "count": self.count, "me_voted": self.me}

    def __repr__(self) -> str:
        return f"<PollAnswerCount is_finalized={self.is_finalized!r}>"


class PollResults:
    """Represents a poll results object.

    .. versionadded:: 2.6

    Attributes
    ----------
    is_finalized: :class:`bool`
        Whether the answer counts have been precicely tallied.
    answer_counts: List[:class:`PollAnswerCount`]
        A list of counts for each answer. If an answer isn't included, it has no votes.
    """

    __slots__ = (
        "is_finalized",
        "answer_counts",
    )

    def __init__(self, data: PollResultsPayload):
        self.is_finalized = data.get("is_finalized")
        self.answer_counts = [
            PollAnswerCount.from_dict(a) for a in data.get("answer_counts", [])
        ]

    def to_dict(self) -> PollAnswerPayload:
        return {
            "is_finalized": self.is_finalized,
            "answer_counts": [a.to_dict() for a in self.answer_counts],
        }

    def __repr__(self) -> str:
        return f"<PollResults is_finalized={self.is_finalized!r}>"


class Poll:
    """Represents a Poll. Polls are sent in regular messages, but note they cannot be sent with any other content or embeds.

    .. versionadded:: 2.6

    Attributes
    ----------
    question: :class:`str`
        The poll's question text.
    answers: List[:class:`PollAnswer`]
        A list of the poll's answers.
    expiry: :class:`datetime.datetime`
        The timestamp that the poll ends at.
    allow_multiselect: :class:`bool`
        Whether multiple answers can be selected.
    layout_type: :class:`PollLayoutType`
        The poll's layout type. Only one exists at the moment.
    results: List[:class:`PollResults`]
        The results from this poll recieved from Discord.
    """

    # note that AutoModActionType.timeout is only valid for trigger type 1?

    __slots__ = (
        "_media",
        "question",
        "answers",
        "expiry",
        "allow_multiselect",
        "layout_type",
        "results",
    )

    def __init__(
        self,
        *,
        question: str,
        answers: List[PollAnswer],
        expiry: datetime.datetime,
        allow_multiselect: bool,
        layout_type: PollLayoutType = PollLayoutType.default,
    ):
        self._media = PollMedia(question)
        self.question: str = question
        self.answers: List[PollAnswer] = answers
        self.expiry: datetime.datetime = expiry
        self.allow_multiselect: bool = allow_multiselect
        self.layout_type: PollLayoutType = layout_type
        self.results = []

    def to_dict(self) -> PollPayload:
        dict_ = {
            "question": self._media.to_dict(),
            "answers": [a.to_dict() for a in self.answers],
            "expiry": self.expiry.strftime(),
            "allow_multiselect": self.allow_multiselect,
            "layout_type": self.layout_type.value,
        }
        if self.results:
            dict_["results"] = [r.to_dict() for r in self.results]
        return dict_

    @classmethod
    def from_dict(cls, data: PollPayload, guild: Guild) -> PollMedia:
        poll = cls(
            question=data["question"]["text"],
            answers=[PollAnswer.from_dict(a) for a in data.get("answers", [])],
            expiry=utils.parse_time(data.get("expiry")),
            allow_multiselect=data.get("allow_multiselect"),
            layout_type=data.get("allow_multiselect"),
        )
        if results := data.get("results", []):
            poll.results = [PollResults.from_dict(r) for r in results]
        return poll

    def __repr__(self) -> str:
        return f"<Poll question={self.question!r}"
