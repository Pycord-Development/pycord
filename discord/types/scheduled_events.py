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

from typing_extensions import NotRequired

from .member import Member
from .snowflake import Snowflake
from .user import User

ScheduledEventStatus = Literal[
    1,  # SCHEDULED
    2,  # ACTIVE
    3,  # COMPLETED
    4,  # CANCELED
]
ScheduledEventEntityType = Literal[
    1,  # STAGE_INSTANCE
    2,  # VOICE
    3,  # EXTERNAL
]
ScheduledEventPrivacyLevel = Literal[2,]  # GUILD_ONLY


class ScheduledEventEntityMetadata(TypedDict):
    location: str  # Technically optional, but this is only sent on EXTERNAL, and then, location is always set


ScheduledEventRecurrenceRuleFrequency = Literal[
    0,  # YEARLY
    1,  # MONTHLY
    2,  # WEEKLY
    3,  # DAILY
]

ScheduledEventRecurrenceRuleWeekday = Literal[
    0,  # MONDAY
    1,  # TUESDAY
    2,  # WEDNESDAY
    3,  # THURSDAY
    4,  # FRIDAY
    5,  # SATURDAY
    6,  # SUNDAY
]

ScheduledEventRecurrenceRuleMonth = Literal[
    1,  # JANUARY
    2,  # FEBRUARY
    3,  # MARCH
    4,  # APRIL
    5,  # MAY
    6,  # JUNE
    7,  # JULY
    8,  # AUGUST
    9,  # SEPTEMBER
    10,  # OCTOBER
    11,  # NOVEMBER
    12,  # DECEMBER
]


class ScheduledEventRecurrenceRuleNWeekday(TypedDict):
    n: int
    day: ScheduledEventRecurrenceRuleWeekday


class ScheduledEventRecurrenceRule(TypedDict):
    start: str
    end: str | None
    frequency: ScheduledEventRecurrenceRuleFrequency
    interval: int
    by_weekday: list[ScheduledEventRecurrenceRuleWeekday] | None
    by_n_weekday: list[ScheduledEventRecurrenceRuleNWeekday] | None
    by_month: list[ScheduledEventRecurrenceRuleMonth] | None
    by_month_day: list[int] | None
    by_year_day: list[int] | None
    count: int | None


class ScheduledEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    channel_id: Snowflake | None
    creator_id: NotRequired[
        Snowflake | None
    ]  # Will be set for events made after Oct 2021
    name: str
    description: NotRequired[str | None]
    scheduled_start_time: str
    scheduled_end_time: str | None  # Required if the type is external
    privacy_level: ScheduledEventPrivacyLevel
    status: ScheduledEventStatus
    entity_type: ScheduledEventEntityType
    entity_id: Snowflake | None
    entity_metadata: ScheduledEventEntityMetadata | None
    creator: NotRequired[User]
    user_count: int
    image: NotRequired[str | None]
    recurrence_rule: NotRequired[str | None]


class ScheduledEventSubscriber(TypedDict):
    guild_scheduled_event_id: Snowflake
    user: User
    member: NotRequired[Member]
