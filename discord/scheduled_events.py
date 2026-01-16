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
from .utils import deprecated, warn_deprecated

__all__ = (
    "ScheduledEvent",
    "ScheduledEventLocation",
    "ScheduledEventEntityMetadata",
)

if TYPE_CHECKING:
    from .abc import Snowflake
    from .channel import StageChannel, VoiceChannel
    from .guild import Guild
    from .member import Member
    from .state import ConnectionState
    from .types.scheduled_events import ScheduledEvent as ScheduledEventPayload
else:
    ConnectionState = None
    StageChannel = None
    VoiceChannel = None

MISSING = utils.MISSING


class ScheduledEventLocation:
    """Represents a scheduled event's location.

    Setting the ``value`` to its corresponding type will set the location type automatically:

    +------------------------+-----------------------------------------------+
    |     Type of Input      |                Location Type                  |
    +========================+===============================================+
    | :class:`StageChannel`  | :attr:`ScheduledEventEntityType.stage_instance` |
    | :class:`VoiceChannel`  | :attr:`ScheduledEventEntityType.voice`          |
    | :class:`str`           | :attr:`ScheduledEventEntityType.external`       |
    +------------------------+-----------------------------------------------+

    .. deprecated:: 2.7
        Use :class:`ScheduledEventEntityMetadata` instead.

    .. versionadded:: 2.0

    Attributes
    ----------
    value: Union[:class:`str`, :class:`StageChannel`, :class:`VoiceChannel`, :class:`Object`]
        The actual location of the scheduled event.
    type: :class:`ScheduledEventEntityType`
        The type of location.
    """

    __slots__ = (
        "_state",
        "value",
    )

    def __init__(
        self,
        *,
        state: ConnectionState | None = None,
        value: str | int | StageChannel | VoiceChannel | None = None,
    ) -> None:
        warn_deprecated("ScheduledEventLocation", "ScheduledEventEntityMetadata", "2.7")
        self._state: ConnectionState | None = state
        self.value: str | StageChannel | VoiceChannel | Object | None
        if value is None:
            self.value = None
        elif isinstance(value, int):
            self.value = (
                self._state.get_channel(id=int(value)) or Object(id=int(value))
                if self._state
                else Object(id=int(value))
            )
        else:
            self.value = value

    def __repr__(self) -> str:
        return f"<ScheduledEventLocation value={self.value!r} type={self.type}>"

    def __str__(self) -> str:
        return str(self.value) if self.value else ""

    @property
    def type(self) -> ScheduledEventEntityType:
        """The type of location."""
        if isinstance(self.value, str):
            return ScheduledEventEntityType.external
        elif self.value.__class__.__name__ == "StageChannel":
            return ScheduledEventEntityType.stage_instance
        elif self.value.__class__.__name__ == "VoiceChannel":
            return ScheduledEventEntityType.voice
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

    def __init__(
        self,
        location: str | None = None,
    ) -> None:
        self.location: str | None = location

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
    scheduled_start_time: :class:`datetime.datetime`
        The time when the event will start
    scheduled_end_time: Optional[:class:`datetime.datetime`]
        The time when the event is supposed to end.
    status: :class:`ScheduledEventStatus`
        The status of the scheduled event.
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
    """

    __slots__ = (
        "id",
        "name",
        "description",
        "scheduled_start_time",
        "scheduled_end_time",
        "status",
        "creator_id",
        "creator",
        "guild",
        "_state",
        "_image",
        "user_count",
        "_cached_subscribers",
        "entity_type",
        "privacy_level",
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
        self.scheduled_start_time: datetime.datetime = datetime.datetime.fromisoformat(
            data.get("scheduled_start_time")
        )
        if scheduled_end_time := data.get("scheduled_end_time", None):
            scheduled_end_time = datetime.datetime.fromisoformat(scheduled_end_time)
        self.scheduled_end_time: datetime.datetime | None = scheduled_end_time
        self.status: ScheduledEventStatus = try_enum(
            ScheduledEventStatus, data.get("status")
        )
        self.entity_type: ScheduledEventEntityType = try_enum(
            ScheduledEventEntityType, data.get("entity_type")
        )
        self.privacy_level: ScheduledEventPrivacyLevel = try_enum(
            ScheduledEventPrivacyLevel, data.get("privacy_level")
        )
        self.channel_id: int | None = utils._get_as_snowflake(data, "channel_id")
        self.entity_id: int | None = utils._get_as_snowflake(data, "entity_id")

        entity_metadata_data = data.get("entity_metadata")
        self.entity_metadata: ScheduledEventEntityMetadata | None = (
            ScheduledEventEntityMetadata(location=entity_metadata_data.get("location"))
            if entity_metadata_data
            else None
        )

        self._cached_subscribers: dict[int, int] = {}
        self.user_count: int | None = data.get("user_count")
        self.creator_id: int | None = utils._get_as_snowflake(data, "creator_id")
        self.creator: Member | None = creator
        self.channel_id = data.get("channel_id", None)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return (
            f"<ScheduledEvent id={self.id} "
            f"name={self.name} "
            f"description={self.description} "
            f"start_time={self.scheduled_start_time} "
            f"end_time={self.scheduled_end_time} "
            f"location={self.location!r} "
            f"status={self.status.name} "
            f"user_count={self.user_count} "
            f"creator_id={self.creator_id}>"
            f"channel_id={self.channel_id}>"
        )

    @property
    @deprecated(instead="entity_metadata.location", since="2.7", removed="3.0")
    def location(self) -> ScheduledEventLocation | None:
        """Returns the location of the event."""
        if self.channel_id is None:
            self.location = ScheduledEventLocation(
                state=self._state, value=self.entity_metadata.location
            )
        else:
            self.location = ScheduledEventLocation(
                state=self._state, value=self.channel_id
            )

    @property
    def created_at(self) -> datetime.datetime:
        """Returns the scheduled event's creation time in UTC."""
        return utils.snowflake_time(self.id)

    @property
    @deprecated(instead="scheduled_start_time", since="2.7", removed="3.0")
    def start_time(self) -> datetime.datetime:
        """
        Returns the scheduled start time of the event.

        .. deprecated:: 2.7
            Use :attr:`scheduled_start_time` instead.
        """
        return self.scheduled_start_time

    @property
    @deprecated(instead="scheduled_end_time", since="2.7", removed="3.0")
    def end_time(self) -> datetime.datetime | None:
        """
        Returns the scheduled end time of the event.

        .. deprecated:: 2.7
            Use :attr:`scheduled_end_time` instead.
        """
        return self.scheduled_end_time

    @property
    @deprecated(instead="user_count", since="2.7", removed="3.0")
    def subscriber_count(self) -> int | None:
        """
        Returns the number of users subscribed to the event.

        .. deprecated:: 2.7
            Use :attr:`user_count` instead.
        """
        return self.user_count

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
        status: ScheduledEventStatus = MISSING,
        location: (
            str | int | VoiceChannel | StageChannel | ScheduledEventLocation
        ) = MISSING,
        entity_type: ScheduledEventEntityType = MISSING,
        scheduled_start_time: datetime.datetime = MISSING,
        scheduled_end_time: datetime.datetime = MISSING,
        image: bytes | None = MISSING,
        cover: bytes | None = MISSING,
        privacy_level: ScheduledEventPrivacyLevel = MISSING,
        entity_metadata: ScheduledEventEntityMetadata | None = MISSING,
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
        scheduled_start_time: :class:`datetime.datetime`
            The new starting time for the event (ISO8601 format).
        scheduled_end_time: :class:`datetime.datetime`
            The new ending time of the event (ISO8601 format).
        privacy_level: :class:`ScheduledEventPrivacyLevel`
            The privacy level of the event. Currently only GUILD_ONLY is supported.
        entity_metadata: Optional[:class:`ScheduledEventEntityMetadata`]
            Additional metadata for the scheduled event.
            When set for EXTERNAL events, must contain a location.
            Will be silently discarded by Discord for non-EXTERNAL events.
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

        if cover is not MISSING:
            warn_deprecated("cover", "image", "2.7", "3.0")
            if image is MISSING:
                image = cover

        if location is not MISSING:
            warn_deprecated("location", "entity_metadata", "2.7", "3.0")
            if entity_metadata is MISSING:
                if not isinstance(location, (ScheduledEventLocation)):
                    location = ScheduledEventLocation(state=self._state, value=location)
                if location.type == ScheduledEventEntityType.external:
                    entity_metadata = ScheduledEventEntityMetadata(str(location))

        if image is not MISSING:
            if image is None:
                payload["image"] = None
            else:
                payload["image"] = utils._bytes_to_base64_data(image)

        if scheduled_start_time is not MISSING:
            payload["scheduled_start_time"] = scheduled_start_time.isoformat()

        if scheduled_end_time is not MISSING:
            payload["scheduled_end_time"] = scheduled_end_time.isoformat()

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

            has_end_time = (
                scheduled_end_time is not MISSING or self.scheduled_end_time is not None
            )
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
