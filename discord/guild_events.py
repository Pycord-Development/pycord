"""
The MIT License (MIT)

Copyright (c) 2015-present Pycord Development

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
    List
)
from .enums import (
    StagePrivacyLevel,
    GuildEventStatus,
    GuildEventEntityType,
    try_enum
)

if TYPE_CHECKING:
    from .state import ConnectionState

class GuildEventEntityMetadata(NamedTuple):
    speaker_ids: Optional[List[int]]
    location: Optional[str]

class GuildEvent:
    def __init__(self, *, data, state: ConnectionState):
        self.id: int = data.get('id')
        self.guild_id: int = data.get('guild_id')
        self.channel_id: int = data.get('channel_id')
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

        # TODO: find out what the following means/does
        self.entity_type: GuildEventEntityType = try_enum(GuildEventEntityType, data.get('entity_tyoe'))
        self.entity_id: int = data.get('entity_id')
        entity_metadata = data.get('entity_metadata')
        self.entity_metadata: GuildEventEntityMetadata = GuildEventEntityMetadata(speaker_ids=entity_metadata.get('speaker_ids', None), location=entity_metadata.get('location', None))
        self.sku_ids = data.get('sku_ids')
        self.skus = data.get('skus')

    @property
    def interested(self):
        return self.user_count
