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

from typing import Literal, TypedDict

from .._typed_dict import NotRequired
from .emoji import Emoji

PollLayoutType = Literal[1]


class PollMedia(TypedDict):
    text: str
    emoji: NotRequired[Emoji]


class PollAnswer(TypedDict):
    answer_id: int
    poll_media: PollMedia


class PollResults(TypedDict):
    is_finalized: bool
    answer_counts: list[PollAnswerCount]


class PollAnswerCount(TypedDict):
    id: int
    count: int
    me_voted: bool


class Poll(TypedDict):
    question: PollMedia
    answers: list[PollAnswer]
    duration: NotRequired[int]
    expiry: NotRequired[str]
    allow_multiselect: bool
    layout_type: NotRequired[PollLayoutType]
    results: NotRequired[PollResults]
