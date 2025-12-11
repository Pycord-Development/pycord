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
from typing import TYPE_CHECKING, Any, Literal

from . import utils
from .asset import Asset
from .enums import (
    ScheduledEventLocationType,
    ScheduledEventPrivacyLevel,
    ScheduledEventRecurrenceFrequency,
    ScheduledEventStatus,
    ScheduledEventWeekday,
    try_enum,
)
from .errors import ClientException, InvalidArgument, ValidationError
from .iterators import ScheduledEventSubscribersIterator
from .mixins import Hashable
from .object import Object
from .utils import warn_deprecated

__all__ = (
    "ScheduledEvent",
    "ScheduledEventLocation",
    "ScheduledEventRecurrenceRule",
)

if TYPE_CHECKING:
    from typing_extensions import Self

    from .abc import Snowflake
    from .guild import Guild
    from .member import Member
    from .state import ConnectionState
    from .types.channel import StageChannel, VoiceChannel
    from .types.scheduled_events import ScheduledEvent as ScheduledEventPayload
    from .types.scheduled_events import (
        ScheduledEventRecurrenceRule as ScheduledEventRecurrenceRulePayload,
    )

    Week = Literal[1, 2, 3, 4, 5]
    WeekDay = Literal[0, 1, 2, 3, 4, 5, 6]
    NWeekDay = tuple[Week, WeekDay]

MISSING = utils.MISSING


class ScheduledEventLocation:
    """Represents a scheduled event's location.

    Setting the ``value`` to its corresponding type will set the location type automatically:

    +------------------------+---------------------------------------------------+
    |     Type of Input      |                   Location Type                   |
    +========================+===================================================+
    | :class:`StageChannel`  | :attr:`ScheduledEventLocationType.stage_instance` |
    | :class:`VoiceChannel`  | :attr:`ScheduledEventLocationType.voice`          |
    | :class:`str`           | :attr:`ScheduledEventLocationType.external`       |
    +------------------------+---------------------------------------------------+

    .. versionadded:: 2.0

    Attributes
    ----------
    value: Union[:class:`str`, :class:`StageChannel`, :class:`VoiceChannel`, :class:`Object`]
        The actual location of the scheduled event.
    type: :class:`ScheduledEventLocationType`
        The type of location.
    """

    __slots__ = (
        "_state",
        "value",
    )

    def __init__(
        self,
        *,
        state: ConnectionState,
        value: str | int | StageChannel | VoiceChannel,
    ):
        self._state = state
        self.value: str | StageChannel | VoiceChannel | Object
        if isinstance(value, int):
            self.value = self._state.get_channel(id=int(value)) or Object(id=int(value))
        else:
            self.value = value

    def __repr__(self) -> str:
        return f"<ScheduledEventLocation value={self.value!r} type={self.type}>"

    def __str__(self) -> str:
        return str(self.value)

    @property
    def type(self) -> ScheduledEventLocationType:
        if isinstance(self.value, str):
            return ScheduledEventLocationType.external
        elif self.value.__class__.__name__ == "StageChannel":
            return ScheduledEventLocationType.stage_instance
        elif self.value.__class__.__name__ == "VoiceChannel":
            return ScheduledEventLocationType.voice


class ScheduledEventRecurrenceRule:
    """Represents a :class:`ScheduledEvent`'s recurrence rule.

    .. versionadded:: 2.7

    Parameters
    ----------
    start_date: :class:`datetime.datetime`
        When will this recurrence rule start.
    frequency: :class:`ScheduledEventRecurrenceFrequency`
        The frequency on which the event will recur.
    interval: :class:`int`
        The spacing between events, defined by ``frequency``.
        Must be ``1`` except if ``frequency`` is :attr:`ScheduledEventRecurrenceFrequency.weekly`,
        in which case it can also be ``2``.
    weekdays: List[Union[:class:`int`, :class:`ScheduledEventWeekday`]]
        The days within a week the event will recur on. Must be between
        0 (Monday) and 6 (Sunday).
        If ``frequency`` is ``2`` this can only have 1 item.
        This is mutally exclusive with ``n_weekdays`` and ``month_days``.
    n_weekdays: List[Tuple[:class:`int`, :class:`int`]]
        A (week, weekday) pairs list that represent the specific day within a
        specific week the event will recur on.
        ``week`` must be between 1 and 5, representing the first and last week of a month
        respectively.
        ``weekday`` must be an integer between 0 (Monday) and 6 (Sunday).
        This is mutually exclusive with ``weekdays`` and ``month_days``.
    month_days: List[:class:`datetime.date`]
        The specific days and months in which the event will recur on. The year will be ignored.
        This is mutually exclusive with ``weekdays`` and ``n_weekdays``.

    Attributes
    ----------
    end_date: Optional[:class:`datetime.datetime`]
        The date on which this recurrence rule will stop.
    count: Optional[:class:`int`]
        The amount of times the event will recur before stopping. Will be ``None``
        if :attr:`ScheduledEventRecurrenceRule.end_date` is ``None``.

    Examples
    --------
    Creating a recurrence rule that repeats every weekday: ::
        rrule = discord.ScheduledEventRecurrenceRule(
            start_date=...,
            frequency=discord.ScheduledEventRecurrenceFrequency.daily,
            interval=1,
            weekdays=[0, 1, 2, 3, 4],  # from monday to friday
        )
    Creating a recurrence rule that repeats every Wednesday: ::
        rrule = discord.ScheduledEventRecurrenceRule(
            start_date=...,
            frequency=discord.ScheduledEventRecurrenceFrequency.weekly,
            interval=1,  # interval must be 1 for the rule to be "every Wednesday"
            weekdays=[2],  # wednesday
        )
    Creating a recurrence rule that repeats every other Wednesday: ::
        rrule = discord.ScheduledEventRecurrenceRule(
            start_date=...,
            frequency=discord.ScheduledEventRecurrenceFrequency.weekly,
            interval=2,  # interval CAN ONLY BE 2 in this context, and makes the rule be "every other Wednesday"
            weekdays=[2],
        )
    Creating a recurrence rule that repeats every month on the fourth Wednesday: ::
        rrule = discord.ScheduledEventRecurrenceRule(
            start_date=...,
            frequency=discord.ScheduledEventRecurrenceFrequency.monthly,
            interval=1,
            n_weekdays=[
                (
                    4,  # fourth week
                    2,  # wednesday
                ),
            ],
        )
    Creating a recurrence rule that repeats anually on July 4: ::
        rrule = discord.ScheduledEventRecurrenceRule(
            start_date=...,
            frequency=discord.ScheduledEventRecurrenceFrequency.yearly,
            month_days=[
                datetime.date(
                    year=1900,  # use a placeholder year, it is ignored anyways
                    month=7,  # July
                    day=4,  # 4th
                ),
            ],
        )
    """

    __slots__ = (
        "start_date",
        "frequency",
        "interval",
        "count",
        "end_date",
        "_weekdays",
        "_n_weekdays",
        "_month_days",
        "_year_days",
        "_state",
    )

    def __init__(
        self,
        start_date: datetime.datetime,
        frequency: ScheduledEventRecurrenceFrequency,
        interval: Literal[1, 2],
        *,
        weekdays: list[WeekDay | ScheduledEventWeekday] = MISSING,
        n_weekdays: list[NWeekDay] = MISSING,
        month_days: list[datetime.date] = MISSING,
    ) -> None:
        self.start_date: datetime.datetime = start_date
        self.frequency: ScheduledEventRecurrenceFrequency = frequency
        self.interval: Literal[1, 2] = interval

        self.count: int | None = None
        self.end_date: datetime.datetime | None = None

        self._weekdays: list[ScheduledEventWeekday] = self._parse_weekdays(weekdays)
        self._n_weekdays: list[NWeekDay] = n_weekdays
        self._month_days: list[datetime.date] = month_days
        self._year_days: list[int] = MISSING

        self._state: ConnectionState | None = None

    def __repr__(self) -> str:
        return f"<ScheduledEventRecurrenceRule start_date={self.start_date} frequency={self.frequency} interval={self.interval}>"

    @property
    def weekdays(self) -> list[ScheduledEventWeekday]:
        """Returns a read-only list containing all the specific days
        within a week on which the event will recur on.
        """
        if self._weekdays is MISSING:
            return []
        return self._weekdays.copy()

    @property
    def n_weekdays(self) -> list[NWeekDay]:
        """Returns a read-only list containing all the specific days
        within a specific week on which the event will recur on.
        """
        if self._n_weekdays is MISSING:
            return []
        return self._n_weekdays.copy()

    @property
    def month_days(self) -> list[datetime.date]:
        """Returns a read-only list containing all the specific days
        within a specific month on which the event will recur on.
        """
        if self._month_days is MISSING:
            return []
        return self._month_days.copy()

    @property
    def year_days(self) -> list[int]:
        """Returns a read-only list containing all the specific days
        of the year on which the event will recur on.
        """
        if self._year_days is MISSING:
            return []
        return self._year_days.copy()

    def copy(self) -> ScheduledEventRecurrenceRule:
        """Creates a stateless copy of this object that allows for
        methods such as :meth:`.edit` to be used on.

        Returns
        -------
        :class:`ScheduledEventRecurrenceRule`
            The recurrence rule copy.
        """

        return ScheduledEventRecurrenceRule(
            start_date=self.start_date,
            frequency=self.frequency,
            interval=self.interval,
            weekdays=self._weekdays,  # pyright: ignore[reportArgumentType]
            n_weekdays=self._n_weekdays,
            month_days=self._month_days,
        )

    def edit(
        self,
        *,
        weekdays: list[WeekDay | ScheduledEventWeekday] | None = MISSING,
        n_weekdays: list[NWeekDay] | None = MISSING,
        month_days: list[datetime.date] | None = MISSING,
    ) -> Self:
        """Edits this recurrence rule.

        If this recurrence rule was obtained from the API you will need to
        :meth:`.copy` it in order to edit it.

        Parameters
        ----------
        weekdays: List[Union[:class:`int`, :class:`ScheduledEventWeekday`]]
            The weekdays the event will recur on. Must be between 0 (Monday) and 6 (Sunday).
        n_weekdays: List[Tuple[:class:`int`, :class:`int`]]
            A (week, weekday) tuple pair list that represents the specific ``weekday``, from 0 (Monday)
            to 6 (Sunday), on ``week`` on which this event will recur on.
        month_days: List[:class:`datetime.date`]
            A list containing the specific day on a month when the event will recur on. The year
            is ignored.

        Returns
        -------
        :class:`ScheduledEventRecurrenceRule`
            The updated recurrence rule.

        Raises
        ------
        ClientException
            You cannot edit this recurrence rule.
        """

        if self._state is not None:
            raise ClientException("You cannot edit this recurrence rule")

        for value, attr in (
            (weekdays, "_weekdays"),
            (n_weekdays, "_n_weekdays"),
            (month_days, "_month_days"),
        ):
            if value is None:
                setattr(self, attr, MISSING)
            elif value is not MISSING:
                if attr == "_weekdays":
                    value = self._parse_weekdays(
                        weekdays
                    )  # pyright: ignore[reportArgumentType]
                setattr(self, attr, value)

        return self

    def _get_month_days_payload(self) -> tuple[list[int], list[int]]:
        months, days = map(list, zip(*((m.month, m.day) for m in self._month_days)))
        return months, days

    def _parse_month_days_payload(
        self, months: list[int], days: list[int]
    ) -> list[datetime.date]:
        return [datetime.date(1, month, day) for month, day in zip(months, days)]

    def _parse_weekdays(
        self, weekdays: list[WeekDay | ScheduledEventWeekday]
    ) -> list[ScheduledEventWeekday]:
        return [
            w if w is ScheduledEventWeekday else try_enum(ScheduledEventWeekday, w)
            for w in weekdays
        ]

    def _get_weekdays(self) -> list[WeekDay]:
        return [w.value for w in self._weekdays]

    @classmethod
    def _from_data(
        cls, data: ScheduledEventRecurrenceRulePayload | None, state: ConnectionState
    ) -> Self | None:
        if data is None:
            return None

        start = utils.parse_time(data["start"])
        end = utils.parse_time(data.get("end"))

        self = cls(
            start_date=start,
            frequency=try_enum(ScheduledEventRecurrenceFrequency, data["frequency"]),
            interval=int(data["interval"]),  # pyright: ignore[reportArgumentType]
        )

        self._state = state
        self.end_date = end
        self.count = data.get("count")

        weekdays = data.get("by_weekday", MISSING) or MISSING
        self._weekdays = self._parse_weekdays(
            weekdays
        )  # pyright: ignore[reportArgumentType]

        n_weekdays = data.get("by_n_weekday", MISSING) or MISSING
        if n_weekdays is not MISSING:
            self._n_weekdays = [(n["n"], n["day"]) for n in n_weekdays]

        months = data.get("by_month")
        month_days = data.get("by_month_day")

        if months and month_days:
            self._month_days = self._parse_month_days_payload(months, month_days)

        year_days = data.get("by_year_day")
        if year_days is not None:
            self._year_days = year_days

        return self

    def _to_dict(self) -> ScheduledEventRecurrenceRulePayload:
        payload: ScheduledEventRecurrenceRulePayload = {
            "start": self.start_date.isoformat(),
            "frequency": self.frequency.value,
            "interval": self.interval,
            "by_weekday": None,
            "by_n_weekday": None,
            "by_month": None,
            "by_month_day": None,
        }

        if self._weekdays is not MISSING:
            payload["by_weekday"] = self._get_weekdays()
        if self._n_weekdays is not MISSING:
            payload["by_n_weekday"] = list(
                map(
                    lambda nw: {"n": nw[0], "day": nw[1]},
                    self._n_weekdays,
                ),
            )
        if self._month_days is not MISSING:
            months, month_days = self._get_month_days_payload()
            payload["by_month"] = months
            payload["by_month_day"] = month_days

        return payload


class ScheduledEvent(Hashable):
    """Represents a Discord Guild Scheduled Event.

    .. container:: operations

        .. describe:: x == y

            Checks if two scheduled events are equal.

        .. describe:: x != y

            Checks if two scheduled events are not equal.

        .. describe:: hash(x)

            Returns the scheduled event's hash.

        .. describe:: str(x)

            Returns the scheduled event's name.

    .. versionadded:: 2.0

    Attributes
    ----------
    guild: :class:`Guild`
        The guild where the scheduled event is happening.
    name: :class:`str`
        The name of the scheduled event.
    description: Optional[:class:`str`]
        The description of the scheduled event.
    start_time: :class:`datetime.datetime`
        The time when the event will start
    end_time: Optional[:class:`datetime.datetime`]
        The time when the event is supposed to end.
    status: :class:`ScheduledEventStatus`
        The status of the scheduled event.
    location: :class:`ScheduledEventLocation`
        The location of the event.
        See :class:`ScheduledEventLocation` for more information.
    subscriber_count: Optional[:class:`int`]
        The number of users that have marked themselves as interested in the event.
    creator_id: Optional[:class:`int`]
        The ID of the user who created the event.
        It may be ``None`` because events created before October 25th, 2021 haven't
        had their creators tracked.
    creator: Optional[:class:`User`]
        The resolved user object of who created the event.
    privacy_level: :class:`ScheduledEventPrivacyLevel`
        The privacy level of the event. Currently, the only possible value
        is :attr:`ScheduledEventPrivacyLevel.guild_only`, which is default,
        so there is no need to use this attribute.
    recurrence_rule: Optional[:class:`ScheduledEventRecurrenceRule`]
        The recurrence rule this scheduled event follows.

        .. versionadded:: 2.7
    exceptions: List[:class:`Object`]
        A list of objects that represents the events on the recurrence rule that were
        cancelled or moved out of it.

        .. versionadded:: 2.7
    """

    __slots__ = (
        "id",
        "name",
        "description",
        "start_time",
        "end_time",
        "status",
        "creator_id",
        "creator",
        "location",
        "guild",
        "_state",
        "_image",
        "subscriber_count",
        "recurrence_rule",
        "exceptions",
    )

    def __init__(
        self,
        *,
        state: ConnectionState,
        guild: Guild,
        creator: Member | None,
        data: ScheduledEventPayload,
    ):
        self._state: ConnectionState = state

        self.id: int = int(data.get("id"))
        self.guild: Guild = guild
        self.name: str = data.get("name")
        self.description: str | None = data.get("description", None)
        self._image: str | None = data.get("image", None)
        self.start_time: datetime.datetime = datetime.datetime.fromisoformat(
            data.get("scheduled_start_time")
        )
        if end_time := data.get("scheduled_end_time", None):
            end_time = datetime.datetime.fromisoformat(end_time)
        self.end_time: datetime.datetime | None = end_time
        self.status: ScheduledEventStatus = try_enum(
            ScheduledEventStatus, data.get("status")
        )
        self.subscriber_count: int | None = data.get("user_count", None)
        self.creator_id: int | None = utils._get_as_snowflake(data, "creator_id")
        self.creator: Member | None = creator

        entity_metadata = data.get("entity_metadata")
        channel_id = data.get("channel_id", None)
        if channel_id is None:
            self.location = ScheduledEventLocation(
                state=state, value=entity_metadata["location"]
            )
        else:
            self.location = ScheduledEventLocation(state=state, value=int(channel_id))

        self.recurrence_rule: ScheduledEventRecurrenceRule | None = (
            ScheduledEventRecurrenceRule._from_data(
                data.get("recurrence_rule"),
                state,
            )
        )
        self.exceptions: list[Object] = list(
            map(
                Object,
                data.get("guild_scheduled_events_exceptions") or [],
            ),
        )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return (
            f"<ScheduledEvent id={self.id} "
            f"name={self.name} "
            f"description={self.description} "
            f"start_time={self.start_time} "
            f"end_time={self.end_time} "
            f"location={self.location!r} "
            f"status={self.status.name} "
            f"subscriber_count={self.subscriber_count} "
            f"creator_id={self.creator_id}>"
        )

    @property
    def created_at(self) -> datetime.datetime:
        """Returns the scheduled event's creation time in UTC."""
        return utils.snowflake_time(self.id)

    @property
    def interested(self) -> int | None:
        """An alias to :attr:`.subscriber_count`"""
        return self.subscriber_count

    @property
    def url(self) -> str:
        """The url to reference the scheduled event."""
        return f"https://discord.com/events/{self.guild.id}/{self.id}"

    @property
    def cover(self) -> Asset | None:
        """
        Returns the scheduled event cover image asset, if available.

        .. deprecated:: 2.7
                Use the :attr:`image` property instead.
        """
        warn_deprecated("cover", "image", "2.7")
        return self.image

    @property
    def image(self) -> Asset | None:
        """Returns the scheduled event cover image asset, if available."""
        if self._image is None:
            return None
        return Asset._from_scheduled_event_image(
            self._state,
            self.id,
            self._image,
        )

    async def edit(
        self,
        *,
        reason: str | None = None,
        name: str = MISSING,
        description: str = MISSING,
        status: int | ScheduledEventStatus = MISSING,
        location: (
            str | int | VoiceChannel | StageChannel | ScheduledEventLocation
        ) = MISSING,
        start_time: datetime.datetime = MISSING,
        end_time: datetime.datetime = MISSING,
        cover: bytes | None = MISSING,
        image: bytes | None = MISSING,
        privacy_level: ScheduledEventPrivacyLevel = ScheduledEventPrivacyLevel.guild_only,
        recurrence_rule: ScheduledEventRecurrenceRule | None = MISSING,
    ) -> ScheduledEvent | None:
        """|coro|

        Edits the Scheduled Event's data

        All parameters are optional unless ``location.type`` is
        :attr:`ScheduledEventLocationType.external`, then ``end_time``
        is required.

        Will return a new :class:`.ScheduledEvent` object if applicable.

        Parameters
        ----------
        name: :class:`str`
            The new name of the event.
        description: :class:`str`
            The new description of the event.
        location: :class:`.ScheduledEventLocation`
            The location of the event.
        status: :class:`ScheduledEventStatus`
            The status of the event. It is recommended, however,
            to use :meth:`.start`, :meth:`.complete`, and
            :meth:`cancel` to edit statuses instead.
        start_time: :class:`datetime.datetime`
            The new starting time for the event.
        end_time: :class:`datetime.datetime`
            The new ending time of the event.
        privacy_level: :class:`ScheduledEventPrivacyLevel`
            The privacy level of the event. Currently, the only possible value
            is :attr:`ScheduledEventPrivacyLevel.guild_only`, which is default,
            so there is no need to change this parameter.
        reason: Optional[:class:`str`]
            The reason to show in the audit log.
        image: Optional[:class:`bytes`]
            The cover image of the scheduled event.
        cover: Optional[:class:`bytes`]
            The cover image of the scheduled event.

            .. deprecated:: 2.7
                Use the `image` argument instead.
        recurrence_rule: Optional[:class:`ScheduledEventRecurrenceRule`]
            The recurrence rule this event will follow, or ``None`` to set it to a
            one-time event.

            .. versionadded:: 2.7

        Returns
        -------
        Optional[:class:`.ScheduledEvent`]
            The newly updated scheduled event object. This is only returned when certain
            fields are updated.

        Raises
        ------
        Forbidden
            You do not have the Manage Events permission.
        HTTPException
            The operation failed.
        """
        payload: dict[str, Any] = {}

        if name is not MISSING:
            payload["name"] = name

        if description is not MISSING:
            payload["description"] = description

        if status is not MISSING:
            payload["status"] = int(status)

        if privacy_level is not MISSING:
            payload["privacy_level"] = int(privacy_level)

        if cover is not MISSING:
            warn_deprecated("cover", "image", "2.7")
            if image is not MISSING:
                raise InvalidArgument(
                    "cannot pass both `image` and `cover` to `ScheduledEvent.edit`"
                )
            else:
                image = cover

        if image is not MISSING:
            if image is None:
                payload["image"] = None
            else:
                payload["image"] = utils._bytes_to_base64_data(image)

        if location is not MISSING:
            if not isinstance(
                location, (ScheduledEventLocation, utils._MissingSentinel)
            ):
                location = ScheduledEventLocation(state=self._state, value=location)

            if location.type is ScheduledEventLocationType.external:
                payload["channel_id"] = None
                payload["entity_metadata"] = {"location": str(location.value)}
            else:
                payload["channel_id"] = location.value.id
                payload["entity_metadata"] = None

            payload["entity_type"] = location.type.value

        location = location if location is not MISSING else self.location
        if end_time is MISSING and location.type is ScheduledEventLocationType.external:
            end_time = self.end_time
            if end_time is None:
                raise ValidationError(
                    "end_time needs to be passed if location type is external."
                )

        if start_time is not MISSING:
            payload["scheduled_start_time"] = start_time.isoformat()

        if end_time is not MISSING:
            payload["scheduled_end_time"] = end_time.isoformat()

        if recurrence_rule is not MISSING:
            if recurrence_rule is None:
                payload["recurrence_rule"] = None
            else:
                payload["recurrence_rule"] = recurrence_rule._to_dict()

        if payload != {}:
            data = await self._state.http.edit_scheduled_event(
                self.guild.id, self.id, **payload, reason=reason
            )
            return ScheduledEvent(
                data=data, guild=self.guild, creator=self.creator, state=self._state
            )

    async def delete(self) -> None:
        """|coro|

        Deletes the scheduled event.

        Raises
        ------
        Forbidden
            You do not have the Manage Events permission.
        HTTPException
            The operation failed.
        """
        await self._state.http.delete_scheduled_event(self.guild.id, self.id)

    async def start(self, *, reason: str | None = None) -> None:
        """|coro|

        Starts the scheduled event. Shortcut from :meth:`.edit`.

        .. note::

            This method can only be used if :attr:`.status` is :attr:`ScheduledEventStatus.scheduled`.

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason to show in the audit log.

        Returns
        -------
        Optional[:class:`.ScheduledEvent`]
            The newly updated scheduled event object.

        Raises
        ------
        Forbidden
            You do not have the Manage Events permission.
        HTTPException
            The operation failed.
        """
        return await self.edit(status=ScheduledEventStatus.active, reason=reason)

    async def complete(self, *, reason: str | None = None) -> ScheduledEvent | None:
        """|coro|

        Ends/completes the scheduled event. Shortcut from :meth:`.edit`.

        .. note::

            This method can only be used if :attr:`.status` is :attr:`ScheduledEventStatus.active`.

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason to show in the audit log.

        Returns
        -------
        Optional[:class:`.ScheduledEvent`]
            The newly updated scheduled event object.

        Raises
        ------
        Forbidden
            You do not have the Manage Events permission.
        HTTPException
            The operation failed.
        """
        return await self.edit(status=ScheduledEventStatus.completed, reason=reason)

    async def cancel(self, *, reason: str | None = None) -> ScheduledEvent | None:
        """|coro|

        Cancels the scheduled event. Shortcut from :meth:`.edit`.

        .. note::

            This method can only be used if :attr:`.status` is :attr:`ScheduledEventStatus.scheduled`.

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason to show in the audit log.

        Returns
        -------
        Optional[:class:`.ScheduledEvent`]
            The newly updated scheduled event object.

        Raises
        ------
        Forbidden
            You do not have the Manage Events permission.
        HTTPException
            The operation failed.
        """
        return await self.edit(status=ScheduledEventStatus.canceled, reason=reason)

    def subscribers(
        self,
        *,
        limit: int | None = 100,
        as_member: bool = False,
        before: Snowflake | datetime.datetime | None = None,
        after: Snowflake | datetime.datetime | None = None,
    ) -> ScheduledEventSubscribersIterator:
        """Returns an :class:`AsyncIterator` representing the users or members subscribed to the event.

        The ``after`` and ``before`` parameters must represent member
        or user objects and meet the :class:`abc.Snowflake` abc.

        .. note::

            Even is ``as_member`` is set to ``True``, if the user
            is outside the guild, it will be a :class:`User` object.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The maximum number of results to return.
        as_member: Optional[:class:`bool`]
            Whether to fetch :class:`Member` objects instead of user objects.
            There may still be :class:`User` objects if the user is outside
            the guild.
        before: Optional[Union[:class:`abc.Snowflake`, :class:`datetime.datetime`]]
            Retrieves users before this date or object. If a datetime is provided,
            it is recommended to use a UTC aware datetime. If the datetime is naive,
            it is assumed to be local time.
        after: Optional[Union[:class:`abc.Snowflake`, :class:`datetime.datetime`]]
            Retrieves users after this date or object. If a datetime is provided,
            it is recommended to use a UTC aware datetime. If the datetime is naive,
            it is assumed to be local time.

        Yields
        ------
        Union[:class:`User`, :class:`Member`]
            The subscribed :class:`Member`. If ``as_member`` is set to
            ``False`` or the user is outside the guild, it will be a
            :class:`User` object.

        Raises
        ------
        HTTPException
            Fetching the subscribed users failed.

        Examples
        --------

        Usage ::

            async for user in event.subscribers(limit=100):
                print(user.name)

        Flattening into a list: ::

            users = await event.subscribers(limit=100).flatten()
            # users is now a list of User...

        Getting members instead of user objects: ::

            async for member in event.subscribers(limit=100, as_member=True):
                print(member.display_name)
        """
        return ScheduledEventSubscribersIterator(
            event=self, limit=limit, with_member=as_member, before=before, after=after
        )
