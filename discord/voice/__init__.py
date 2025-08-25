"""
discord.voice
~~~~~~~~~~~~~

Voice support for the Discord API.

:copyright: (c) 2015-2021 Rapptz & 2021-present Pycord Development
:license: MIT, see LICENSE for more details.
"""

from ._types import VoiceProtocol
from .client import VoiceClient

__all__ = (
    "VoiceClient",
    "VoiceProtocol",
)
