"""
discord.voice
~~~~~~~~~~~~~

Voice support for the Discord API.

:copyright: (c) 2015-2021 Rapptz & 2021-present Pycord Development
:license: MIT, see LICENSE for more details.
"""

from ..errors import MissingVoiceDependenciesError
from ..utils import get_missing_voice_dependencies

if _missing := get_missing_voice_dependencies():
    raise MissingVoiceDependenciesError(missing=_missing)

from ._types import *
from .client import *
from .packets import *
