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
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union
from .enums import (
    ScheduledEventPrivacyLevel,
    ScheduledEventStatus,
    ScheduledEventLocationType,
    try_enum
)
from .utils import MISSING
from .mixins import Hashable
from .iterators import ScheduledEventSubscribersIterator

__all__ = (
    'ScheduledEvent',
    'ScheduledEventLocation',
)

if TYPE_CHECKING:
    from .abc import Snowflake
    from .state import ConnectionState
    from .member import Member
    from .iterators import AsyncIterator
    from .types.guild import Guild
    from .types.scheduled_events import ScheduledEvent as ScheduledEventPayload
    from .types.channel import StageChannel, VoiceChannel

class ScheduledEventLocation:
    """Represents a scheduled event's location.

    Setting the ``location`` to its corresponding type will set the location type automatically:
    - :class:`StageChannel`: :attr:`.ScheduledEventLocationType.external`
    - :class:`VoiceChannel`: :attr:`.ScheduledEventLocationType.voice`
    - :class:`str`: :attr:`.ScheduledEventLocationType.external`

    .. versionadded:: 2.0

    Attributes
    ----------
    value: Union[:class:`str`, :class:`int`, :class:`StageChannel`, :class:`VoiceChannel`]
        The actual location of the scheduled event.
    type: :class:`ScheduledEventLocationType`
        The type of location.
    """

    __slots__ = (
        '_state',
        'value',
    )

    def __init__(self, *, state: ConnectionState, location: Union[str, int, StageChannel, VoiceChannel]):
        self._state = state
        if isinstance(location, int):
            self.value = self._state._get_channel(int(location))
        else:
            self.value = location
    
    @property
    def type(self):
        if isinstance(self.value, str):
            return ScheduledEventLocationType.external
        elif self.value.__class__.__name__ == "StageChannel":
            return ScheduledEventLocationType.stage_instance
        elif self.value.__class__.__name__ == "VoiceChannel":
            return ScheduledEventLocationType.voice


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
    user_count: Optional[:class:`int`]
        The number of users that have marked themselves as interested for the event.
    interested: Optional[:class:`int`]
        Alias to :attr:`user_count`
    creator_id: Optional[:class:`int`]
        The ID of the user who created the event.
        It may be ``None`` because events created before October 25th, 2021, haven't
        had their creators tracked.
    creator: Optional[:class:`User`]
        The resolved user object of who created the event.
    location: :class:`ScheduledEventLocation`
        The location of the event.
        See :class:`ScheduledEventLocation` for more information.
    guild: :class:`Guild`
        The guild where the scheduled event is happening.
    """
    
    __slots__ = (
        'id',
        'name',
        'description',
        'start_time',
        'end_time',
        'status',
        'creator_id',
        'creator',
        'location',
        'guild',
        '_state',
        'user_count',
    )

    def __init__(self, *, state: ConnectionState, guild: Guild, creator: Optional[Member], data: ScheduledEventPayload):
        self._state = state
        
        self.id: int = int(data.get('id'))
        self.guild: Guild = guild
        self.name: str = data.get('name')
        self.description: Optional[str] = data.get('description', None)
        #self.image: Optional[str] = data.get('image', None) # Waiting on documentation 
        self.start_time: datetime.datetime = datetime.datetime.fromisoformat(data.get('scheduled_start_time'))
        end_time = data.get('scheduled_end_time', None)
        if end_time != None:
            end_time = datetime.datetime.fromisoformat(end_time)
        self.end_time: Optional[datetime.datetime] = end_time
        self.status: ScheduledEventStatus = try_enum(ScheduledEventStatus, data.get('status'))
        self.user_count: Optional[int] = data.get('user_count', None)
        self.creator_id = data.get('creator_id', None)
        self.creator: Optional[Member] = creator

        entity_metadata = data.get('entity_metadata')
        channel_id = data.get('channel_id', None)
        if channel_id != None:
            self.location = ScheduledEventLocation(state=state, location=channel_id)
        else:
            self.location = ScheduledEventLocation(state=state, location=entity_metadata["location"])

    @property
    def interested(self):
        """An alias to :attr:`.user_count`"""
        return self.user_count
    
    async def edit(
        self,
        *,
        name: str = MISSING,
        description: str = MISSING,
        status: Union[int, ScheduledEventStatus] = MISSING,
        location: Union[str, int, VoiceChannel, StageChannel, ScheduledEventLocation] = MISSING,
        start_time: datetime.datetime = MISSING,
        end_time: datetime.datetime = MISSING,
        privacy_level: ScheduledEventPrivacyLevel = ScheduledEventPrivacyLevel.guild_only,
    ) -> Optional[ScheduledEvent]:
        """|coro|
        
        Edits the Scheduled Event's data
        
        All parameters are optional
        
        Will return a new :class:`.ScheduledEvent` object if applicable.
        
        Parameters
        -----------
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

        Raises
        -------
        Forbidden
            You do not have the Manage Events permission.
        HTTPException
            The operation failed.

        Returns
        --------
        Optional[:class:`.ScheduledEvent`]
            The newly updated scheduled event object. This is only returned when certain
            fields are updated.
        """
        payload: Dict[str, Any] = {}

        if name is not MISSING:
            payload["name"] = name

        if description is not MISSING:
            payload["description"] = description

        if status is not MISSING:
            payload["status"] = int(status)

        if privacy_level is not MISSING:
            payload["privacy_level"] = int(privacy_level)

        if not isinstance(location, ScheduledEventLocation):
            location = ScheduledEventLocation(state=self._state, location=location)

        if location is not MISSING:
            if location.type in (ScheduledEventLocationType.voice, ScheduledEventLocationType.stage_instance):
                payload["channel_id"] = location.value.id
                payload["entity_metadata"] = None
            else:
                payload["channel_id"] = None
                payload["entity_metadata"] = {"location":str(location.value)}

        if start_time is not MISSING:
            payload["scheduled_start_time"] = start_time.isoformat()
        
        if end_time is not MISSING:
            payload["scheduled_end_time"] = end_time.isoformat()

        if payload != {}:
            data = await self._state.http.edit_scheduled_event(self.guild.id, self.id, **payload)
            return ScheduledEvent(data=data, guild=self.guild, creator=self.creator, state=self._state)

    async def delete(self) -> None:
        """|coro|
        
        Deletes the scheduled event.

        Raises
        -------
        Forbidden
            You do not have the Manage Events permission.
        HTTPException
            The operation failed.

        """
        await self._state.http.delete_scheduled_event(self.guild.id, self.id)

    async def start(self) -> None:
        """|coro|

        Starts the scheduled event. Shortcut from :meth:`.edit`.

        Raises
        -------
        Forbidden
            You do not have the Manage Events permission.
        HTTPException
            The operation failed.

        Returns
        --------
        Optional[:class:`.ScheduledEvent`]
            The newly updated scheduled event object. This is only returned when certain
            fields are updated.
        """
        return await self.edit(status=ScheduledEventStatus.active)

    async def complete(self) -> None:
        """|coro|

        Ends/completes the scheduled event. Shortcut from :meth:`.edit`.

        Raises
        -------
        Forbidden
            You do not have the Manage Events permission.
        HTTPException
            The operation failed.

        Returns
        --------
        Optional[:class:`.ScheduledEvent`]
            The newly updated scheduled event object. This is only returned when certain
            fields are updated.
        """
        return await self.edit(status=ScheduledEventStatus.completed)

    async def cancel(self) -> None:
        """|coro|

        Cancels the scheduled event. Shortcut from :meth:`.edit`.

        Raises
        -------
        Forbidden
            You do not have the Manage Events permission.
        HTTPException
            The operation failed.

        Returns
        --------
        Optional[:class:`.ScheduledEvent`]
            The newly updated scheduled event object. This is only returned when certain
            fields are updated.
        """
        return await self.edit(status=ScheduledEventStatus.canceled)

    async def users(
        self,
        limit: Optional[int] = None,
        as_member: bool = False,
        before: Optional[Snowflake] = None,
        after: Optional[Snowflake] = None,
    ) -> AsyncIterator:
        """Returns an :class:`AsyncIterator` representing the users (or members depending on the ``as_member`` parameter) subscribed to the event.
        """
        return ScheduledEventSubscribersIterator(event=self, limit=limit, with_member=as_member, before=before, after=after)
