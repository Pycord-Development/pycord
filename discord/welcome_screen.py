"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

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

from typing import TYPE_CHECKING, List, Union
from .utils import _get_as_snowflake, get

if TYPE_CHECKING:
    from .types.welcome_screen import (
        WelcomeScreen as WelcomeScreenPayload,
        WelcomeScreenChannel as WelcomeScreenChannelPayload,
    )
    from .guild import Guild
    from .abc import Snowflake
    from .partial_emoji import PartialEmoji
    from .emoji import Emoji

__all__ = (
    'WelcomeScreen',
    'WelcomeScreenChannel',
)

class WelcomeScreenChannel:
    """Represents a welcome channel displayed on :class:`WelcomeScreen`
    
    .. versionadded:: 2.0

    Attributes
    ----------

    channel: :class:`abc.Snowflake`
        The channel that is being referenced.
    description: :class:`str`
        The description of channel that is shown on the welcome screen.
    emoji: :class:`Union[Emoji, PartialEmoji, str]`
        The emoji of channel that is shown on welcome screen.
    """
    def __init__(self, channel: Snowflake, description: str, emoji: Union[Emoji, PartialEmoji, str]):
        self.channel = channel
        self.description = description
        self.emoji = emoji

    def to_dict(self) -> WelcomeScreenChannelPayload:
        dict_: WelcomeScreenChannelPayload = {
            'channel_id': self.channel.id,
            'description': self.description,
            'emoji_id': None,
            'emoji_name': None,
        }

        if isinstance(self.emoji, (PartialEmoji, Emoji)):
            # custom guild emoji
            dict_['emoji_id'] = self.emoji.id  # type: ignore
            dict_['emoji_name'] = self.emoji.name  # type: ignore
        else:
            # unicode emoji or None
            dict_['emoji_name'] = self.emoji
            dict_['emoji_id'] = None # type: ignore

        return dict_

    
    @classmethod
    def _from_dict(cls, data: WelcomeScreenChannelPayload, guild: Guild) -> WelcomeChannel:
        channel_id = _get_as_snowflake(data, 'channel_id')
        channel = guild.get_channel(channel_id)
        description = data['description']
        _emoji_id = _get_as_snowflake(data, 'emoji_id')
        _emoji_name = data['emoji_name']

        if _emoji_id:
            # custom guild emoji
            emoji = get(guild.emojis, id=_emoji_id)
        else:
            # unicode emoji or None
            emoji = _emoji_name

        return cls(channel=channel, description=description, emoji=emoji)  # type: ignore



class WelcomeScreen:
    """Represents the welcome screen of a guild.

    .. versionadded:: 2.0
    
    Attributes
    ----------
    
    description: :class:`str`
        The description text displayed on the welcome screen.
    welcome_channels: List[:class:`WelcomeScreenChannel`]
        A list of channels displayed on welcome screen.
    """
    __slots__ = ('description', 'welcome_channels')

    def __init__(self, data: WelcomeScreenPayload, guild: Guild):
        self._guild = guild
        self._update(data)
    
    def _update(self, data: WelcomeScreenPayload):
        self.description: str = data.get('description')
        self.welcome_channels: List[WelcomeScreenChannel] = [WelcomeScreenChannel._from_dict(channel) for channel in data.get('welcome_channels', [])]
    

    @property
    def enabled(self) -> bool:
        """:class:`bool`: Indicates whether the welcome screen is enabled or not."""
        return 'WELCOME_SCREEN_ENABLED' in self._guild.features

    @property
    def guild(self) -> Guild:
        """:class:`Guild`: The guild this welcome screen belongs to."""
        return self._guild

