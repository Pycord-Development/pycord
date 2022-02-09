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

import datetime
from typing import TYPE_CHECKING, List, NamedTuple

if TYPE_CHECKING:
    from .state import ConnectionState
    from .guild import Guild

class DiscoveryMetadata:
    def __init__(self, *, state: ConnectionState, guild: Guild, data):
        self._state: ConnectionState = state

        self.guild: Guild = guild
        self.primary_category_id: int = data.get('primary_category_id')
        self.keywords: List[str] = data.get('keywords', [])
        self.emoji_discoverability_enabled: bool = data.get('emoji_discoverability_enabled')
        self.partner_application: datetime.datetime = datetime.datetime.fromisoformat(data.get('partner_application_timestamp')) if data.get('partner_application_timestamp', None) is not None else None
        self.partner_actioned: datetime.datetime = datetime.datetime.fromisoformat(data.get('partner_actioned_timestamp')) if data.get('partner_actioned_timestamp', None) is not None else None
        self.category_ids: List[int] = data.get('category_ids')

class DiscoveryName:
    def __init__(self, data):
        self.default = data.get('default')
        self.localizations = data.get('localizations', None)

class DiscoveryCategory:
    def __init__(self, *, state: ConnectionState, data):  # TODO: check if state is needed
        self._state: ConnectionState = state

        self.id: int = data.get('id')
        self.name: str = DiscoveryName(data = data.get('name'))
        self.is_primary: bool = data.get('is_primary')
