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
    ScheduledEventStatus,
    ScheduledEventLocationType,
    try_enum
)
from .channel import VoiceChannel, StageChannel
from .utils import MISSING
from .mixins import Hashable
from .user import User

__all__ = (
    'ScheduledEvent',
    'ScheduledEventLocation',
)

if TYPE_CHECKING:
    from .state import ConnectionState
    from .types.guild import Guild
    from .types.scheduled_events import ScheduledEvent as ScheduledEventPayload

class ScheduledEventLocation:
    """Represents a scheduled event's location.

    Setting the ``location`` to its corresponding type will set the location type automatically:
    - :class:`StageChannel`: :attr:`.ScheduledEventLocationType.external`
    - :class:`VoiceChannel`: :attr:`.ScheduledEventLocationType.voice`
    - :class:`str`: :attr:`.ScheduledEventLocationType.external`

    .. versionadded:: 2.1

    Attributes
    ----------
    value: Union[:class:`str`, :class:`int`, :class:`StageChannel`, :class:`VoiceChannel`]
        The actual location of the scheduled event.
    type: :class:`ScheduledEventLocationType`
        The type of location.
    """

    __slots__ = (
        'value',
        'type',
    )

    def __init__(self, *, state: ConnectionState, location: Union[str, int, VoiceChannel, StageChannel]):
        self._state = state
        if isinstance(location, int):
            self.value = self._state._get_channel(int(location))
        else:
            self.value = location
    
    @property
    def type(self):
        if isinstance(self.value, StageChannel):
            return ScheduledEventLocationType.stage_instance
        elif isinstance(self.value, VoiceChannel):
            return ScheduledEventLocationType.voice
        else:
            return ScheduledEventLocationType.external


class ScheduledEvent(Hashable):
    """Represents a Discord Guild Scheduled Event.

    .. versionadded:: 2.1

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
        It may be ``None`` because events created before October 25th, 2021, haven't had their creators tracked.
    creator: Optional[:class:`User`]
        The resolved user object of who created the event.
    location: :class:`ScheduledEventLocation`
        The location of the event.
        See :class:`ScheduledEventLocation` for more information.
    guild: :class:`Guild`
        The guild where the scheduled event is happening.
    """
    
    __slots__ = (
        'name',
        'description',
        'start_time',
        'end_time',
        'status',
        'creator_id',
        'creator',
        'location',
        'guild',
    )

    def __init__(self, *, state: ConnectionState, guild: Guild, data: ScheduledEventPayload):
        self._state = state
        
        self.id: int = data.get('id')
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
        self.creator = User(state=self._state, data=data.get('creator', None))

        entity_metadata = data.get('entity_metadata')
        entity_type = try_enum(ScheduledEventLocationType, data.get('entity_type'))
        channel_id = data.get('channel_id', None)
        if channel_id != None:
            self.location = ScheduledEventLocation(state=state, location=channel_id, type=entity_type)
        else:
            self.location = ScheduledEventLocation(state=state, location=entity_metadata["location"], type=entity_type)

        # TODO: find out what the following means/does
        self.entity_id: int = data.get('entity_id')

    @property
    def interested(self):
        return self.user_count
    
    async def edit(
        self,
        *,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        location: ScheduledEventLocation = MISSING,
        start_time: datetime.datetime = MISSING,
        end_time: datetime.datetime = MISSING,
    ) -> Optional[ScheduledEvent]:
        """|coro|
        
        Edits the Scheduled Event's data
        
        All parameters are optional
        
        Will return a new :class:`.ScheduledEvent` object if applicable.
        
        Parameters
        ----------
        name: Optional[:class:`str`]
            The new name of the event.
        description: Optional[:class:`str`]
            The new description of the event.
        channel_id: :class:`int`
            The id of the new channel the event will be taking place.
        start_time: :class:`datetime.datetime`
            The new starting time for the event.

        Raises
        ------
        Forbidden
            You do not have the Manage Events permission.
        HTTPException
            The operation failed.

        Returns
        -------
        Optional[:class:`.ScheduledEvent`]
            The newly updated scheduled event object. This is only returned when certain
            fields are updated.
        """
        payload: Dict[str, Any] = {}

        if name is not MISSING:
            payload["name"] = name

        if description is not MISSING:
            payload["description"] = description

        if location is not MISSING:
            if location.type in (ScheduledEventLocationType.voice, ScheduledEventLocationType.stage_instance):
                payload["channel_id"] = location.location.id
                payload["entity_metadata"] = None
            else:
                payload["channel_id"] = None
                payload["entity_metadata"] = {"location":str(location.location)}

        if start_time is not MISSING:
            payload["scheduled_start_time"] = start_time.isoformat()
        
        if end_time is not MISSING:
            payload["scheduled_end_time"] = end_time.isoformat()

        if payload != {}:
            data = await self._state.http.edit_scheduled_event(self.id, **payload)
            return ScheduledEvent(data=data, state=self._state)

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
        await self._state.http.delete_scheduled_event(self.id)

    async def users(self):
        pass # TODO: discord/abc.py#1587
