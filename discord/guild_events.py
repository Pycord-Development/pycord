add cover foto
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

# NOTE: This is a work in progress
# plus the endpoints aren't available yet

from __future__ import annotations

import datetime
from typing import (
    TYPE_CHECKING,
    Optional,
    NamedTuple,
    List,
    Dict,
    Any
)
from .enums import (
    StagePrivacyLevel,
    GuildEventStatus,
    GuildEventLocationType,
    try_enum
)
from .channel import VoiceChannel, StageChannel
from .utils import MISSING

if TYPE_CHECKING:
    from .state import ConnectionState
    from .types.guild import Guild

class GuildEventEntityMetadata(NamedTuple):
    speaker_ids: Optional[List[int]]
    location: Optional[str]

class GuildEventLocation:
    def __init__(self, *, state: ConnectionState, location, type: GuildEventLocationType):
        self._state = state
        if type in (GuildEventLocationType.voice, GuildEventLocationType.stage_instance):
            self.location = self._state._get_channel(int(location))
        else:
            self.location = location
    
    @property
    def type(self):
        if isinstance(self.location, StageChannel):
            return GuildEventLocationType.stage_instance
        elif isinstance(self.location, VoiceChannel):
            return GuildEventLocationType.voice
        else:
            return GuildEventLocationType.external


class GuildEvent:
    # TODO: remove speaker_ids
    def __init__(self, *, data, state: ConnectionState):
        self._state = state
        
        self.id: int = data.get('id')
        self.guild: Guild = self._state._get_guild(int(data.get('guild_id')))
        #self.channel_id: int = data.get('channel_id', None)
        self.name: str = data.get('name')
        self.description: Optional[str] = data.get('description', None)
        self.image: Optional[str] = data.get('image', None) # Waiting on documentation 
        self.start_time: datetime.datetime = datetime.datetime.fromisoformat(data.get('scheduled_start_time'))
        end_time = data.get('scheduled_end_time', None)
        if end_time != None:
            end_time = datetime.datetime.fromisoformat(end_time)
        self.end_time: Optional[datetime.datetime] = end_time
        self.privacy_level: StagePrivacyLevel = try_enum(StagePrivacyLevel, data.get('privacy_level'))
        self.status: GuildEventStatus = try_enum(GuildEventStatus, data.get('status'))
        self.user_count: Optional[int] = data.get('user_count', None)
        self.creator_id = data.get('creator_id', None)
        self.creator = data.get('creator', None) # TODO: Convert

        entity_metadata = data.get('entity_metadata')
        entity_type = try_enum(GuildEventLocationType, data.get('entity_type'))
        channel_id = data.get('channel_id', None)
        if channel_id != None:
            self.location = GuildEventLocation(state=state, location=channel_id, type=entity_type)
        else:
            self.location = GuildEventLocation(state=state, location=entity_metadata.location, type=entity_type)
        if entity_metadata.speaker_ids != None:
            self.speaker_ids = entity_metadata.speaker_ids

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
        location: GuildEventLocation = MISSING,
        speaker_ids: List[int] = MISSING,
        privacy_level: StagePrivacyLevel = MISSING,
        start_time: datetime.datetime = MISSING,
    ) -> Optional[GuildEvent]:
        """|coro|
        
        Edits the Guild Event's data
        
        All parameters are optional
        
        Will return a new :class:`.GuildEvent` object if applicable.
        
        Parameters
        ----------
        name: Optional[:class:`str`]
            The new name of the event.
        description: Optional[:class:`str`]
            The new description of the event.
        channel_id: :class:`int`
            The id of the new channel the event will be taking place.
        privacy_level: :class:`.StagePrivacyLevel`
            The new privacy level of this event (if it's happening in a stage channel).
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
        Optional[:class:`.GuildEvent`]
            The newly updated guild event object. This is only returned when certain
            fields are updated.
        """
        # TODO:
        # for `channel_id` it may become optional because
        # there's a custom location parameter so it might
        # not be giving us an ID in the first place

        payload: Dict[str, Any] = {}

        if name is not MISSING:
            payload["name"] = name

        if description is not MISSING:
            payload["description"] = description

        if privacy_level is not MISSING:
            payload["privacy_level"] = privacy_level.value

        if speaker_ids is MISSING:
            speaker_ids = []

        if location is not MISSING:
            if location.type in (GuildEventLocationType.voice, GuildEventLocationType.stage_instance):
                payload["channel_id"] = location.location.id
                payload["entity_metadata"] = {"speaker_ids":speaker_ids, "location":str(location.location.id)}
            else:
                payload["entity_metadata"] = {"speaker_ids":speaker_ids, "location":str(location.location)}

        if start_time is not MISSING:
            payload["scheduled_start_time"] = start_time.isoformat()

        if payload != {}:
            data = await self._state.http.edit_guild_event(self.id, **payload)
            return GuildEvent(data=data, state=self._state)

    async def delete(self) -> None:
        """|coro|
        
        Deletes the guild event.

        Raises
        ------
        Forbidden
            You do not have the Manage Events permission.
        HTTPException
            The operation failed.
        """
        await self._state.http.delete_guild_event(self.id)
