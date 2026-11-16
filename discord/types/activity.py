"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
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

from typing import Literal

from typing_extensions import NotRequired, TypedDict

from .snowflake import Snowflake
from .user import PartialUser

StatusType = Literal["idle", "dnd", "online", "offline"]


class PresenceUpdate(TypedDict):
    """The presence update *can* always be partial in that it contains a user with at least the id"""

    user: PartialUser
    guild_id: Snowflake
    status: StatusType
    activities: list[Activity]
    client_status: ClientStatus


class ClientStatus(TypedDict):
    """Received from the gateway"""

    desktop: NotRequired[str]
    mobile: NotRequired[str]
    web: NotRequired[str]
    vr: NotRequired[str]


class ActivityTimestamps(TypedDict):
    """Received from the gateway as part of an :class:`Activity` object"""

    start: NotRequired[int]
    end: NotRequired[int]


class ActivityParty(TypedDict):
    """Received from the gateway as part of an :class:`Activity` object"""

    id: NotRequired[str]
    size: NotRequired[list[int]]


class ActivityAssets(TypedDict):
    """Received from the gateway as part of an :class:`Activity` object"""

    large_image: NotRequired[str]
    large_text: NotRequired[str]
    large_url: NotRequired[str]
    small_image: NotRequired[str]
    small_text: NotRequired[str]
    small_url: NotRequired[str]
    invite_cover_image: NotRequired[str]


class ActivitySecrets(TypedDict):
    """Received from the gateway as part of an :class:`Activity` object"""

    join: NotRequired[str]
    spectate: NotRequired[str]
    match: NotRequired[str]


class ActivityEmoji(TypedDict):
    """Received from the gateway as part of an :class:`Activity` object"""

    id: NotRequired[Snowflake]
    animated: NotRequired[bool]
    name: str


class ActivityButton(TypedDict):
    """Received from the gateway as part of an :class:`Activity` object"""

    label: str
    url: str


ActivityType = Literal[0, 1, 2, 3, 4, 5]


class SendableActivity(TypedDict):
    """Partial :class:`Activity` object that can be sent to the gateway, bot users can only set these fields"""

    name: str
    type: ActivityType
    url: NotRequired[str | None]
    state: NotRequired[str | None]


class Activity(SendableActivity):
    """The full :class:`Activity` object received from the gateway"""

    created_at: int
    timestamps: NotRequired[ActivityTimestamps]
    application_id: NotRequired[Snowflake]
    status_display_type: NotRequired[int | None]
    details: NotRequired[str | None]
    details_url: NotRequired[str | None]
    state: NotRequired[str | None]
    state_url: NotRequired[str | None]
    emoji: NotRequired[ActivityEmoji | None]
    party: NotRequired[ActivityParty]
    assets: NotRequired[ActivityAssets]
    secrets: NotRequired[ActivitySecrets]
    instance: NotRequired[bool]
    flags: NotRequired[int]
    buttons: NotRequired[
        list[str]
    ]  # Technically an :class:`ActivityButton` object. Over the gateway, these are sent as strings
