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

from typing import TYPE_CHECKING

from typing_extensions import deprecated

"""
since discord.voice raises an error when importing it without having the
required package (ie davey) installed, we can't import it in __init__ because
that would break the whole library, that is why this file is here.

the error would still be raised, but at least here we have more freedom on how we are typing it
"""
__all__ = ("VoiceProtocol", "VoiceClient")

if TYPE_CHECKING:
    from discord.voice import (
        VoiceClient,
        VoiceProtocol,
    )
else:

    @deprecated(
        "discord.VoiceClient is deprecated since version 2.7.0, consider using discord.voice.VoiceClient instead."
    )
    def VoiceClient(*args, **kwargs):
        from discord.voice import VoiceClient

        return VoiceClient(*args, **kwargs)

    @deprecated(
        "discord.VoiceProtocol is deprecated since version 2.8.0, consider using discord.voice.VoiceProtocol instead."
    )
    def VoiceProtocol(*args, **kwargs):
        from discord.voice import VoiceProtocol

        return VoiceProtocol(*args, **kwargs)
