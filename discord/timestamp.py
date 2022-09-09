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

import types
from collections import namedtuple
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)
from datetime import datetime
from .enums import TimestampType

__all__ = (
    "Timestamp",
)


class Timestamp:
    """Represents a Discord timestamp.

    This class lets you create a formatted timesamp for Discord messages.

    Parameters
        ----------
        value: Optional[:class:`int`, :class:`float`, :class:`datetime.datetime`]
            The timestamp either as int, float or datetime object.
        type: :class:`TimestampType`
            Type of the Discord timestamp.

        Returns
        --------
        :class:`str`
            Formatted timestamp ready to send in a message.
    """

    __slots__ = (
        "value",
        "type"
    )

    def __init__(
        self,
        value: Union[int, float, datetime] = datetime.now(),
        type: TimestampType = TimestampType.SHORT_DATETIME
    ):
        self.value = value
        self.type = type

    def __str__(self):
        if isinstance(self.value, int):
            int_timestamp = self.value

        elif isinstance(self.value, float):
            int_timestamp = int(self.value)

        elif isinstance(self.value, datetime):
            int_timestamp = int(self.value.timestamp())

        return f"<t:{int_timestamp}{self.type.value}>"