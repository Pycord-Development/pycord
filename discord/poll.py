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
from .enums import PollLayoutType, try_enum
from .iterators import VoteIterator
from .partial_emoji import PartialEmoji

__all__ = (
    "PollMedia",
    "PollAnswer",
    "PollAnswerCount",
    "PollResults",
    "Poll",
)


if TYPE_CHECKING:
    from .abc import Snowflake
    from .emoji import Emoji
    from .message import Message, PartialMessage
    from .types.poll import Poll as PollPayload
    from .types.poll import PollAnswer as PollAnswerPayload
    from .types.poll import PollAnswerCount as PollAnswerCountPayload
    from .types.poll import PollMedia as PollMediaPayload
    from .types.poll import PollResults as PollResultsPayload


class PollMedia:
    """Represents a poll media object that supports both questions and answers.

    .. versionadded:: 2.6

    Attributes
    ----------
    text: :class:`str`
        The question/answer text. May have up to 300 characters for questions and 55 characters for answers.

    emoji: Optional[Union[:class:`Emoji`, :class:`PartialEmoji`, :class:`str`]]
        The answer's emoji.
    """

    def __init__(self, text: str, emoji: Emoji | PartialEmoji | str | None = None):
        self.text: str = text
        self.emoji: Emoji | PartialEmoji | str | None = emoji

    def to_dict(self) -> PollMediaPayload:
        dict_ = {
            "text": self.text,
        }
        if self.emoji:
            if isinstance(self.emoji, str):
                dict_["emoji"] = {
                    "name": self.emoji,
                }
            else:
                if self.emoji.id:
                    dict_["emoji"] = {
                        "id": str(self.emoji.id),
                    }
                else:
                    dict_["emoji"] = {"name": self.emoji.name}

        return dict_

    @classmethod
    def from_dict(
        cls, data: PollMediaPayload, message: Message | PartialMessage | None = None
    ) -> PollMedia:

        _emoji: dict[str, Any] = data.get("emoji") or {}
        if isinstance(_emoji, dict) and _emoji.get("name"):
            emoji = PartialEmoji.from_dict(_emoji)
            if emoji.id and message:
                emoji = message._state.get_emoji(emoji.id) or emoji
        else:
            emoji = _emoji or None
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
    media: :class:`PollMedia`
        The relevant media for this answer.
    """

    def __init__(self, text: str, emoji: Emoji | PartialEmoji | str | None = None):
        self.media = PollMedia(text, emoji)
        self.id = None
        self._poll = None

    @property
    def text(self) -> str:
        """The answer's text. Shortcut for :attr:`PollMedia.text`."""
        return self.media.text

    @property
    def emoji(self) -> Emoji | PartialEmoji | None:
        """The answer's emoji. Shortcut for :attr:`PollMedia.emoji`."""
        return self.media.emoji

    @property
    def count(self) -> int | None:
        """This answer's vote count, if recieved from Discord."""
        if not (self._poll and self.id):
            return None
        if self._poll.results is None:
            return None  # Unknown vote count.
        _count = self._poll.results and utils.get(
            self._poll.results.answer_counts, id=self.id
        )
        if _count:
            return _count.count
        return 0  # If an answer isn't in answer_counts, it has 0 votes.

    def to_dict(self) -> PollAnswerPayload:
        dict_ = {
            "poll_media": self.media.to_dict(),
        }
        if self.id is not None:
            dict_["answer_id"] = (self.id,)
        return dict_

    @classmethod
    def from_dict(
        cls,
        data: PollAnswerPayload,
        poll=None,
        message: Message | PartialMessage | None = None,
    ) -> PollAnswer:
        media = PollMedia.from_dict(data["poll_media"], message=message)
        answer = cls(
            media.text,
            media.emoji,
        )
        answer.id = data["answer_id"]
        answer._poll = poll
        return answer

    def __repr__(self) -> str:
        return f"<PollAnswer id={self.id!r} text={self.text!r} emoji={self.emoji!r}>"

    def voters(
        self, *, limit: int | None = None, after: Snowflake | None = None
    ) -> VoteIterator:
        """Returns an :class:`AsyncIterator` representing the users that have voted with this answer.
        Only works if this poll was recieved from Discord.

        The ``after`` parameter must represent a member
        and meet the :class:`abc.Snowflake` abc.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The maximum number of results to return.
            If not provided, returns all the users who
            voted with this answer.
        after: Optional[:class:`abc.Snowflake`]
            For pagination, answers are sorted by member.

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
        RuntimeError
            This poll wasn't recieved from a message.

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

        if not self._poll or not self._poll._message:
            raise RuntimeError(
                "Users can only be fetched from an existing message poll."
            )

        if limit is None:
            limit = self.count or 100  # Ambiguous

        return VoteIterator(self._poll._message, self, limit, after)


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

    def __init__(self, data: PollAnswerCountPayload):
        self.id = data["id"]
        self.count: int = data.get("count", 0)
        self.me = data.get("me_voted")

    def to_dict(self) -> PollAnswerCountPayload:
        return {"id": self.id, "count": self.count, "me_voted": self.me}

    def __repr__(self) -> str:
        return f"<PollAnswerCount id={self.id!r} count={self.count!r} me={self.me!r}>"


class PollResults:
    """Represents a poll results object.

    .. versionadded:: 2.6

    Attributes
    ----------
    is_finalized: :class:`bool`
        Whether the poll has ended and all answer counts have been precisely tallied.

    answer_counts: List[:class:`PollAnswerCount`]
        A list of counts for each answer. If an answer isn't included, it has no votes.
    """

    def __init__(self, data: PollResultsPayload):
        self.is_finalized = data.get("is_finalized")
        self._answer_counts = {
            a["id"]: PollAnswerCount(a) for a in data.get("answer_counts", [])
        }

    def to_dict(self) -> PollResultsPayload:
        return {
            "is_finalized": self.is_finalized,
            "answer_counts": [a.to_dict() for a in self.answer_counts],
        }

    def __repr__(self) -> str:
        return f"<PollResults is_finalized={self.is_finalized!r} total_votes={self.total_votes()!r}>"

    @property
    def answer_counts(self) -> list[PollAnswerCount]:
        return list(self._answer_counts.values())

    def total_votes(self) -> int:
        """
        Get the total number of votes across all answers. This may not be accurate if :attr:`is_finalized` is ``False``.

        Returns
        -------
        :class:`int`
            The total number of votes on this poll.
        """
        return sum([a.count for a in self.answer_counts])


class Poll:
    """Represents a Poll. Polls are sent in regular messages, and you must have :attr:`~discord.Permissions.send_polls` to send them.

    .. versionadded:: 2.6

    Attributes
    ----------
    question: Union[:class:`PollMedia`, :class:`str`]
        The poll's question media, or a ``str`` representing the question text. Question text can be up to 300 characters.
    answers: Optional[List[:class:`PollAnswer`]]
        A list of the poll's answers. A maximum of 10 answers can be set.
    duration: :class:`int`
        The number of hours until this poll expires. Users must specify this when creating a poll, but existing polls return :attr:`expiry` instead. Defaults to 24.
    allow_multiselect: :class:`bool`
        Whether multiple answers can be selected. Defaults to ``False``.
    layout_type: :class:`PollLayoutType`
        The poll's layout type. Only one exists at the moment.
    results: Optional[:class:`PollResults`]
        The results of this poll recieved from Discord. If ``None``, this should be considered "unknown" rather than "no" results.
    """

    def __init__(
        self,
        question: PollMedia | str,
        *,
        answers: list[PollAnswer] | None = None,
        duration: int | None = 24,
        allow_multiselect: bool | None = False,
        layout_type: PollLayoutType | None = PollLayoutType.default,
    ):
        self.question = (
            question if isinstance(question, PollMedia) else PollMedia(question)
        )
        self.answers: list[PollAnswer] = answers or []
        self.duration: int | None = duration
        self.allow_multiselect: bool = allow_multiselect
        self.layout_type: PollLayoutType = layout_type
        self.results = None
        self._expiry = None
        self._message = None

    @utils.cached_property
    def expiry(self) -> datetime.datetime | None:
        """An aware datetime object that specifies the date and time in UTC when the poll will end."""
        return utils.parse_time(self._expiry)

    def to_dict(self) -> PollPayload:
        dict_ = {
            "question": self.question.to_dict(),
            "answers": [a.to_dict() for a in self.answers],
            "duration": self.duration,
            "allow_multiselect": self.allow_multiselect,
            "layout_type": self.layout_type.value,
        }
        if self.results:
            dict_["results"] = [r.to_dict() for r in self.results]
        if self._expiry:
            dict_["expiry"] = self._expiry
        return dict_

    @classmethod
    def from_dict(
        cls, data: PollPayload, message: Message | PartialMessage | None = None
    ) -> Poll:
        if not data:
            return None
        poll = cls(
            question=PollMedia.from_dict(data["question"], message=message),
            answers=[
                PollAnswer.from_dict(a, message=message)
                for a in data.get("answers", [])
            ],
            duration=data.get("duration"),
            allow_multiselect=data.get("allow_multiselect"),
            layout_type=try_enum(PollLayoutType, data.get("layout_type", 1)),
        )
        if (results := data.get("results")) is not None:
            poll.results = PollResults(results)
        elif message and message.poll:
            # results is nullable, so grab old results if necessary.
            poll.results = message.poll.results
        poll._expiry = data.get("expiry")
        poll._message = message
        for a in poll.answers:
            a._poll = poll
        return poll

    def __repr__(self) -> str:
        return f"<Poll question={self.question!r} total_answers={len(self.answers)} expiry={(self._expiry)!r} allow_multiselect={self.allow_multiselect!r}>"

    def has_ended(self) -> bool | None:
        """
        Checks if this poll has completely ended. Shortcut for :attr:`PollResults.is_finalized`, if available.

        Returns
        -------
        Optional[:class:`bool`]
            Returns a boolean if :attr:`results` is available, otherwise ``None``.
        """
        if not self.results:
            return None
        return self.results.is_finalized

    def total_votes(self) -> int | None:
        """
        Shortcut for :meth:`PollResults.total_votes` This may not be precise if :attr:`is_finalized` is ``False``.

        Returns
        -------
        Optional[:class:`int`]
            The total number of votes on this poll if :attr:`results` is available, otherwise ``None``.
        """
        if not self.results:
            return None
        return self.results.total_votes()

    def get_answer(self, id) -> PollAnswer | None:
        """
        Get a poll answer by ID.

        Parameters
        ----------
        id: :class:`int`
            The ID to search for.

        Returns
        -------
        Optional[:class:`.PollAnswer`]
            The returned answer or ``None`` if not found.
        """
        return utils.get(self.answers, id=id)

    def add_answer(
        self, text: str, *, emoji: Emoji | PartialEmoji | str | None = None
    ) -> Poll:
        """Add an answer to this poll.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        ----------
        text: :class:`str`
            The answer text. Maximum 55 characters.
        emoji: Optional[Union[:class:`Emoji`, :class:`PartialEmoji`, :class:`str`]]
            The answer's emoji.

        Raises
        ------
        ValueError
            The poll already has 10 answers or ``text`` exceeds the character length.
        RuntimeError
            You cannot add an answer to an existing poll.

        Examples
        --------

        Regular usage ::

            poll = Poll(
                question=PollMedia("What's your favorite color?"),

                answers=[PollAnswer("Red", "❤")]
                duration=24,
                allow_multiselect=False
            )
            poll.add_answer(text="Green", emoji="💚")
            poll.add_answer(text="Blue", emoji="💙")

        Chaining style ::

            poll = Poll("What's your favorite color?").add_answer("Red", emoji="❤").add_answer("Green").add_answer("Blue")
        """
        if len(self.answers) >= 10:
            raise ValueError("Polls may only have up to 10 answers.")
        if len(text) > 55:
            raise ValueError("text length must be between 1 and 55 characters.")
        if self.expiry or self._message:
            raise RuntimeError("You cannot add answers to an existing poll.")

        self.answers.append(PollAnswer(text, emoji))
        return self

    async def end(self) -> Message:
        """
        Immediately ends this poll, if attached to a message. Only doable by the poll's owner.
        Shortcut to :meth:`Message.end_poll`

        Returns
        -------
        :class:`Message`
            The updated message.

        Raises
        ------
        Forbidden
            You do not have permissions to end this poll.
        HTTPException
            Ending this poll failed.
        RuntimeError
            This poll wasn't recieved from a message.
        """

        if not self._message:
            raise RuntimeError("You can only end a poll recieved from a message.")

        return await self._message.end_poll()
