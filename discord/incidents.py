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
from typing import TYPE_CHECKING

from .utils import parse_time

if TYPE_CHECKING:
    from .types.guild import IncidentsData as IncidentsDataPayload

__all__ = ("IncidentsData",)


class IncidentsData:
    """Represents the incidents data object for a guild.

    Attributes
    ----------
    invites_disabled_until: Optional[datetime.datetime]
        When invites will be enabled again as a :class:`datetime.datetime`, or ``None``.
    dms_disabled_until: Optional[datetime.datetime]
        When direct messages will be enabled again as a :class:`datetime.datetime`, or ``None``.
    dm_spam_detected_at: Optional[datetime.datetime]
        When DM spam was detected, or ``None``.
    raid_detected_at: Optional[datetime.datetime]
        When a raid was detected, or ``None``.
    """

    __slots__ = (
        "invites_disabled_until",
        "dms_disabled_until",
        "dm_spam_detected_at",
        "raid_detected_at",
    )

    def __init__(self, data: IncidentsDataPayload):
        self.invites_disabled_until: datetime.datetime | None = parse_time(
            data.get("invites_disabled_until")
        )

        self.dms_disabled_until: datetime.datetime | None = parse_time(
            data.get("dms_disabled_until")
        )

        self.dm_spam_detected_at: datetime.datetime | None = parse_time(
            data.get("dm_spam_detected_at")
        )

        self.raid_detected_at: datetime.datetime | None = parse_time(
            data.get("raid_detected_at")
        )

    def to_dict(self) -> IncidentsDataPayload:
        return {
            "invites_disabled_until": self.invites_disabled_until
            and self.invites_disabled_until.isoformat(),
            "dms_disabled_until": self.dms_disabled_until
            and self.dms_disabled_until.isoformat(),
            "dm_spam_detected_at": self.dm_spam_detected_at
            and self.dm_spam_detected_at.isoformat(),
            "raid_detected_at": self.raid_detected_at
            and self.raid_detected_at.isoformat(),
        }
