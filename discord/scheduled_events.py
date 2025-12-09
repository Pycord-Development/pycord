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
from .asset import Asset
from .enums import (
    ScheduledEventEntityType,
    ScheduledEventPrivacyLevel,
    ScheduledEventStatus,
    try_enum,
)
from .errors import ValidationError
from .iterators import ScheduledEventSubscribersIterator
from .mixins import Hashable
from .object import Object
from .utils import warn_deprecated

__all__ = (
    "ScheduledEvent",
    "ScheduledEventLocation",
    "ScheduledEventEntityMetadata",
)

if TYPE_CHECKING:
    from .abc import Snowflake
    from .guild import Guild
    from .member import Member
    from .state import ConnectionState
    from .types.channel import StageChannel, VoiceChannel
    from .types.scheduled_events import ScheduledEvent as ScheduledEventPayload

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
    def type(self) -> ScheduledEventEntityType:
        if isinstance(self.value, str):
            return ScheduledEventEntityType.external
        elif self.value.__class__.__name__ == "StageChannel":
            return ScheduledEventEntityType.stage_instance
        elif self.value.__class__.__name__ == "VoiceChannel":
            return ScheduledEventEntityType.voice


class ScheduledEventEntityMetadata:
    """Represents a scheduled event's entity metadata.

    This contains additional metadata for the scheduled event, particularly
    for external events which require a location string.

    .. versionadded:: 2.7

    Attributes
    ----------
    location: Optional[:class:`str`]
        The location of the event (1-100 characters). Only present for EXTERNAL events.
    """

    __slots__ = ("location",)

    def __init__(self, *, data: dict[str, str]) -> str | None:
        self.location: str | None = data.get("location")

    def __repr__(self) -> str:
        return f"<ScheduledEventEntityMetadata location={self.location!r}>"

    def __str__(self) -> str:
        return self.location or ""

    def to_payload(self) -> dict[str, str]:
        """Converts the entity metadata to a Discord API payload.

        Returns
        -------
        dict[str, str]
            A dictionary with the entity metadata fields for the API.
        """
        return {"location": self.location}


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
    user_count: :class:`int`
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
    entity_type: :class:`ScheduledEventEntityType`
        The type of scheduled event (STAGE_INSTANCE, VOICE, or EXTERNAL).
    entity_id: Optional[:class:`int`]
        The ID of an entity associated with the scheduled event.
    entity_metadata: Optional[:class:`ScheduledEventEntityMetadata`]
        Additional metadata for the scheduled event (e.g., location for EXTERNAL events).
    recurrence_rule: Optional[:class:`dict`]
        The definition for how often this event should recur.
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
        "user_count",
        "_cached_subscribers",
        "entity_type",
        "privacy_level",
        "recurrence_rule",
        "channel_id",
        "entity_id",
        "entity_metadata",
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
        self.entity_type: ScheduledEventEntityType = try_enum(
            ScheduledEventEntityType, data.get("entity_type")
        )
        self.privacy_level: ScheduledEventPrivacyLevel = try_enum(
            ScheduledEventPrivacyLevel, data.get("privacy_level")
        )
        self.recurrence_rule: dict | None = data.get("recurrence_rule", None)
        self.channel_id: int | None = utils._get_as_snowflake(data, "channel_id")
        self.entity_id: int | None = utils._get_as_snowflake(data, "entity_id")

        entity_metadata_data = data.get("entity_metadata")
        self.entity_metadata: ScheduledEventEntityMetadata | None = (
            ScheduledEventEntityMetadata(data=entity_metadata_data)
            if entity_metadata_data
            else None
        )

        self._cached_subscribers: dict[int, int] = {}
        self.user_count: int | None = data.get("user_count")
        self.creator_id: int | None = utils._get_as_snowflake(data, "creator_id")
        self.creator: Member | None = creator

        channel_id = data.get("channel_id", None)
        if channel_id is None and entity_metadata_data:
            self.location = ScheduledEventLocation(
                state=state, value=entity_metadata_data["location"]
            )
        else:
            self.location = ScheduledEventLocation(state=state, value=int(channel_id))

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
            f"user_count={self.user_count} "
            f"creator_id={self.creator_id}>"
        )

    @property
    def created_at(self) -> datetime.datetime:
        """Returns the scheduled event's creation time in UTC."""
        return utils.snowflake_time(self.id)

    @property
    def interested(self) -> int | None:
        """An alias to :attr:`.user_count`"""
        return self.user_count

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
        entity_type: ScheduledEventEntityType = MISSING,
        start_time: datetime.datetime = MISSING,
        end_time: datetime.datetime = MISSING,
        cover: bytes | None = MISSING,
        image: bytes | None = MISSING,
        privacy_level: ScheduledEventPrivacyLevel = MISSING,
        entity_metadata: ScheduledEventEntityMetadata | None = MISSING,
        recurrence_rule: dict = MISSING,
    ) -> ScheduledEvent | None:
        """|coro|

        Edits the Scheduled Event's data.

        All parameters are optional.

        .. note::

            When changing entity_type to EXTERNAL via entity_metadata, Discord will
            automatically set ``channel_id`` to null.

        .. note::

            The Discord API silently discards ``entity_metadata`` for non-EXTERNAL events.

        Will return a new :class:`.ScheduledEvent` object if applicable.

        Parameters
        ----------
        name: :class:`str`
            The new name of the event (1-100 characters).
        description: :class:`str`
            The new description of the event (1-1000 characters).
        status: :class:`ScheduledEventStatus`
            The status of the event. It is recommended, however,
            to use :meth:`.start`, :meth:`.complete`, and
            :meth:`.cancel` to edit statuses instead.
            Valid transitions: SCHEDULED → ACTIVE, ACTIVE → COMPLETED, SCHEDULED → CANCELED.
        entity_type: :class:`ScheduledEventEntityType`
            The type of scheduled event. When changing to EXTERNAL, you must also provide
            ``entity_metadata`` with a location and ``scheduled_end_time``.
        start_time: :class:`datetime.datetime`
            The new starting time for the event (ISO8601 format).
        end_time: :class:`datetime.datetime`
            The new ending time of the event (ISO8601 format).
        privacy_level: :class:`ScheduledEventPrivacyLevel`
            The privacy level of the event. Currently only GUILD_ONLY is supported.
        entity_metadata: Optional[:class:`ScheduledEventEntityMetadata`]
            Additional metadata for the scheduled event.
            When set for EXTERNAL events, must contain a location.
            Will be silently discarded by Discord for non-EXTERNAL events.
        recurrence_rule: :class:`dict`
            The definition for how often this event should recur.
        reason: Optional[:class:`str`]
            The reason to show in the audit log.
        image: Optional[:class:`bytes`]
            The cover image of the scheduled event.

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
        ValidationError
            Invalid parameters for the event type.
        """
        payload: dict[str, Any] = {}

        if name is not MISSING:
            payload["name"] = name

        if description is not MISSING:
            payload["description"] = description

        if status is not MISSING:
            payload["status"] = int(status)

        if entity_type is not MISSING:
            payload["entity_type"] = int(entity_type)

        if privacy_level is not MISSING:
            payload["privacy_level"] = int(privacy_level)

        if entity_metadata is not MISSING:
            if entity_metadata is None:
                payload["entity_metadata"] = None
            else:
                payload["entity_metadata"] = entity_metadata.to_payload()

        if recurrence_rule is not MISSING:
            payload["recurrence_rule"] = recurrence_rule

        if image is not MISSING:
            if image is None:
                payload["image"] = None
            else:
                payload["image"] = utils._bytes_to_base64_data(image)

        if start_time is not MISSING:
            payload["scheduled_start_time"] = start_time.isoformat()

        if end_time is not MISSING:
            payload["scheduled_end_time"] = end_time.isoformat()

        if (
            entity_type is not MISSING
            and entity_type == ScheduledEventEntityType.external
        ):
            if entity_metadata is MISSING or entity_metadata is None:
                raise ValidationError(
                    "entity_metadata with a location is required when entity_type is EXTERNAL."
                )
            if not entity_metadata.location:
                raise ValidationError(
                    "entity_metadata.location cannot be empty for EXTERNAL events."
                )

            has_end_time = end_time is not MISSING or self.end_time is not None
            if not has_end_time:
                raise ValidationError(
                    "scheduled_end_time is required for EXTERNAL events."
                )

            payload["channel_id"] = None

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

    async def complete(self, *, reason: str | None = None) -> None:
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

    async def cancel(self, *, reason: str | None = None) -> None:
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
        use_cache: bool = False,
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
        use_cache: Optional[:class:`bool`]
            If ``True``, only use cached subscribers and skip API calls.
            This is useful when calling from an event handler where the
            event may have been deleted. Defaults to ``False``.

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

        Using only cached subscribers (e.g., in a delete event handler): ::

            async for member in event.subscribers(limit=100, as_member=True, use_cache=True):
                print(member.display_name)
        """
        return ScheduledEventSubscribersIterator(
            event=self,
            limit=limit,
            with_member=as_member,
            before=before,
            after=after,
            use_cache=use_cache,
        )
