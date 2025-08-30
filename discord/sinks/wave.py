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
import wave
from typing import TYPE_CHECKING, Literal, overload

from discord.file import File
from discord.utils import MISSING

from .core import RawData, Sink, SinkFilter, SinkHandler
from .enums import SinkFilteringMode
from .errors import NoUserAdio

if TYPE_CHECKING:
    from discord import abc

__all__ = (
    "WaveConverterHandler",
    "WavConverterHandler",
    "WaveSink",
    "WavSink",
)


class WaveConverterHandler(SinkHandler["WaveSink"]):
    """Default handler to add received voice packets to the audio cache data in
    a :class:`~.WaveSink`.

    .. versionadded:: 2.7
    """

    def handle_packet(
        self, sink: WaveSink, user: abc.Snowflake, packet: RawData
    ) -> None:
        data = sink.get_user_audio(user.id) or sink._create_audio_packet_for(user.id)
        data.write(packet.decoded_data)


WavConverterHandler: SinkHandler[WavSink] = WaveConverterHandler  # type: ignore
"""An alias for :class:`~.WaveConverterHandler`

.. versionadded:: 2.7
"""


class WaveSink(Sink):
    """A special sink for .wav(e) files.

    This is essentially a :class:`~.Sink` with a :class:`.WaveConverterHandler` handler.

    .. versionadded:: 2.0

    Parameters
    ----------
    filters: List[:class:`~.SinkFilter`]
        The filters to apply to this sink recorder.
    filtering_mode: :class:`~.SinkFilteringMode`
        How the filters should work. If set to :attr:`~.SinkFilteringMode.all`, all filters must go through
        in order for an audio packet to be stored in this sink, else if it is set to :attr:`~.SinkFilteringMode.any`,
        only one filter is required to return ``True`` in order for an audio packet to be stored in this sink.
    handlers: List[:class:`~.SinkHandler`]
        The sink handlers. Handlers are objects that are called after filtering, and that can be used to, for example
        store a certain packet data in a file, or local mapping.
    """

    def __init__(
        self,
        *,
        filters: list[SinkFilter] = MISSING,
        filtering_mode: SinkFilteringMode = SinkFilteringMode.all,
        handlers: list[SinkHandler] = MISSING,
    ) -> None:
        self.__audio_data: dict[int, io.BytesIO] = {}
        handlers = handlers or []
        handlers.append(WaveConverterHandler())

        super().__init__(
            filters=filters,
            filtering_mode=filtering_mode,
            handlers=handlers,
        )

    def get_user_audio(self, user_id: int) -> io.BytesIO | None:
        """Gets a user's saved audiop data, or ``None``."""
        return self.__audio_data.get(user_id)

    def _create_audio_packet_for(self, uid: int) -> io.BytesIO:
        data = self.__audio_data[uid] = io.BytesIO()
        return data

    @overload
    def format_user_audio(
        self,
        user_id: int,
        *,
        as_file: Literal[True],
    ) -> File: ...

    @overload
    def format_user_audio(
        self,
        user_id: int,
        *,
        as_file: Literal[False] = ...,
    ) -> io.BytesIO: ...

    def format_user_audio(
        self,
        user_id: int,
        *,
        as_file: bool = False,
    ) -> io.BytesIO | File:
        """Formats a user's saved audio data.

        This should be called after the bot has stopped recording.

        If this is called during recording, there could be missing audio
        packets.

        After this, the user's audio data will be resetted to 0 bytes and
        seeked to 0.

        Parameters
        ----------
        user_id: :class:`int`
            The user ID of which format the audio data into a file.
        as_file: :class:`bool`
            Whether to return a :class:`~discord.File` object instead of a :class:`io.BytesIO`.

        Returns
        -------
        Union[:class:`io.BytesIO`, :class:`~discord.File`]
            The user's audio saved bytes, if ``as_file`` is ``False``, else a :class:`~discord.File`
            object with the buffer set as the audio bytes.

        Raises
        ------
        NoUserAudio
            You tried to format the audio of a user that was not stored in this sink.
        """

        try:
            data = self.__audio_data.pop(user_id)
        except KeyError:
            raise NoUserAdio

        decoder = self.client.decoder

        with wave.open(data, "wb") as f:
            f.setnchannels(decoder.CHANNELS)
            f.setsampwidth(decoder.SAMPLE_SIZE // decoder.CHANNELS)
            f.setframerate(decoder.SAMPLING_RATE)

        data.seek(0)

        if as_file:
            return File(data, filename=f"{user_id}-recording.pcm")
        return data

    def cleanup(self) -> None:
        for _, buffer in self.__audio_data.items():
            if not buffer.closed:
                buffer.close()

        self.__audio_data.clear()
        super().cleanup()


WavSink = WaveSink
"""An alias for :class:`~.WaveSink`.

.. versionadded:: 2.7
"""
