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

from ._types import VoiceProtocol


class VoiceClient(VoiceProtocol):
    """Represents a Discord voice connection.

    You do not create these, you typically get them from e.g. :meth:`VoiceChannel.connect`.

    Attributes
    ----------
    session_id: :class:`str`
        The voice connection session ID. You should not share this.
    token: :class:`str`
        The voice connection token. You should not share this.
    endpoint: :class:`str`
        The endpoint the current client is connected to.
    channel: :class:`abc.Connectable`
        The voice channel connected to.
    loop: :class:`asyncio.AbstractEventLoop`
        The event loop that the voice client is running on.

    Warning
    -------
    In order to use PCM based AudioSources, you must have the opus library
    installed on your system and loaded through :func:`opus.load_opus`.
    Otherwise, your AudioSources must be opus encoded (e.g. using :class:`FFmpegOpusAudio`)
    or the library will not be able to transmit audio.
    """
