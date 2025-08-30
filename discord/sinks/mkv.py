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
import subprocess
import time
from collections import deque
from typing import TYPE_CHECKING, Literal, overload

from discord.file import File
from discord.utils import MISSING

from .core import RawData, Sink, SinkFilter, SinkHandler
from .enums import SinkFilteringMode
from .errors import FFmpegNotFound, MaxProcessesCountReached, MKVSinkError, NoUserAdio

if TYPE_CHECKING:
    from discord import abc

_log = logging.getLogger(__name__)

__all__ = (
    "MKVConverterHandler",
    "MKVSink",
)


class MKVConverterHandler(SinkHandler["MKVSink"]):
    """Default handler to add received voice packets to the audio cache data in
    a :class:`~.MKVSink`.
    
    .. versionadded:: 2.7
    """

    def handle_packet(
        self, sink: MKVSink, user: abc.Snowflake, packet: RawData
    ) -> None:
        data = sink.get_user_audio(user.id) or sink._create_audio_packet_for(user.id)
        data.write(packet.decoded_data)


class MKVSink(Sink):
    """A special sink for .mkv files.

    This is essentially a :class:`~.Sink` with a :class:`~.MKVConverterHandler` handler
    passed as a default.

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
    max_audio_processes_count: :class:`int`
        The maximum of audio conversion processes that can be active concurrently. If this limit is exceeded, then
        when calling methods like :meth:`.format_user_audio` they will raise :exc:`MaxProcessesCountReached`.
    """

    def __init__(
        self,
        *,
        filters: list[SinkFilter] = MISSING,
        filtering_mode: SinkFilteringMode = SinkFilteringMode.all,
        handlers: list[SinkHandler] = MISSING,
        max_audio_processes_count: int = 10,
    ) -> None:
        self.__audio_data: dict[int, io.BytesIO] = {}
        self.__process_queue: deque[subprocess.Popen] = deque(
            maxlen=max_audio_processes_count
        )
        handlers = handlers or []
        handlers.append(MKVConverterHandler())

        super().__init__(
            filters=filters,
            filtering_mode=filtering_mode,
            handlers=handlers,
        )

    def get_user_audio(self, user_id: int) -> io.BytesIO | None:
        """Gets a user's saved audio data, or ``None``."""
        return self.__audio_data.get(user_id)

    def _create_audio_packet_for(self, uid: int) -> io.BytesIO:
        data = self.__audio_data[uid] = io.BytesIO()
        return data

    @overload
    def format_user_audio(
        self,
        user_id: int,
        *,
        executable: str = ...,
        as_file: Literal[True],
    ) -> File: ...

    @overload
    def format_user_audio(
        self,
        user_id: int,
        *,
        executable: str = ...,
        as_file: Literal[False] = ...,
    ) -> io.BytesIO: ...

    def format_user_audio(
        self,
        user_id: int,
        *,
        executable: str = "ffmpeg",
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
        executable: :class:`str`
            The FFmpeg executable path to use for this formatting. It defaults
            to ``ffmpeg``.
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
        FFmpegNotFound
            The provided FFmpeg executable was not found.
        MaxProcessesCountReached
            You tried to go over the maximum processes count threshold.
        MKVSinkError
            Any error raised while formatting, wrapped around MKVSinkError.
        """

        if len(self.__process_queue) >= 10:
            raise MaxProcessesCountReached

        try:
            data = self.__audio_data.pop(user_id)
        except KeyError:
            _log.info("There is no audio data for %s, ignoring.", user_id)
            raise NoUserAdio

        args = [
            executable,
            "-f",
            "s16le",
            "-ar",
            "48000",
            "-loglevel",
            "error",
            "-ac",
            "2",
            "-i",
            "-",
            "-f",
            "matroska",
            "pipe:1",
        ]

        try:
            process = subprocess.Popen(
                args, stdin=subprocess.PIPE, stdout=subprocess.PIPE
            )
            self.__process_queue.append(process)
        except FileNotFoundError as exc:
            raise FFmpegNotFound from exc
        except subprocess.SubprocessError as exc:
            raise MKVSinkError(f"Audio formatting for user {user_id} failed") from exc

        out = process.communicate(data.read())[0]
        buffer = io.BytesIO(out)
        buffer.seek(0)

        try:
            self.__process_queue.remove(process)
        except ValueError:
            pass

        if as_file:
            return File(buffer, filename=f"{user_id}-{time.time()}-recording.mkv")
        return buffer

    def _clean_process(self, process: subprocess.Popen) -> None:
        _log.debug("Cleaning process %s for sink %s", process, self)
        process.kill()

    def cleanup(self) -> None:
        for process in self.__process_queue:
            self._clean_process(process)
        self.__process_queue.clear()

        for _, buffer in self.__audio_data.items():
            if not buffer.closed:
                buffer.close()

        self.__audio_data.clear()
        super().cleanup()
