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

import io
import logging
import wave
from typing import TYPE_CHECKING

from discord.opus import Decoder
from discord.file import File

from .core import Sink
if TYPE_CHECKING:
    from discord import abc
    from discord.voice import VoiceData

_log = logging.getLogger(__name__)

__all__ = (
    "WaveSink",
    "WavSink",
)


class WaveSink(Sink):
    """A special sink for .wav(e) files.

    .. versionadded:: 2.0

    Parameters
    ----------
    destination: :class:`str` | :term:`py:bytes-like object`
        The destination in which the data should be saved into.

        If this is a filename, then it is saved into that. Else, treats
        it like a buffer.

        .. versionadded:: 2.7
    channels: :class:`int`
        The amount of channels.

        .. versionadded:: 2.7
    sample_width: :class:`int`
        The sample width to "n" bytes.

        .. versionadded:: 2.7
    sampling_rate: :class:`int`
        The frame rate. A non-integral input is rounded to the nearest int.

        .. versionadded:: 2.7
    """

    def __init__(
        self,
        destination: wave._File,
        *,
        channels: int = Decoder.CHANNELS,
        sample_width: int = Decoder.SAMPLE_SIZE // Decoder.CHANNELS,
        sampling_rate: int = Decoder.SAMPLING_RATE,
    ) -> None:
        super().__init__()

        self._destination: wave._File = destination
        self._file: wave.Wave_write = wave.open(destination, "wb")
        self._file.setnchannels(channels)
        self._file.setsampwidth(sample_width)
        self._file.setframerate(sampling_rate)

    def is_opus(self) -> bool:
        return False

    def write(self, user: abc.User | None, data: VoiceData) -> None:
        self._file.writeframes(data.pcm)

    def to_file(self, filename: str, /, *, description: str | None = None, spoiler: bool = False) -> File | None:
        """Returns the :class:`discord.File` of this sink.

        .. warning::

            This should be used only after the sink has stopped recording.
        """

        f = wave.open(self._destination, "rb")
        data = f.readframes(f.getnframes())
        return File(io.BytesIO(data), filename, description=description, spoiler=spoiler)

    def cleanup(self) -> None:
        try:
            self._file.close()
        except Exception as exc:
            _log.warning("An error ocurred while closing the wave writing file on cleanup", exc_info=exc)


WavSink = WaveSink
"""An alias for :class:`~.WaveSink`.

.. versionadded:: 2.7
"""
