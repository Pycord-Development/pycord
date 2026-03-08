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

import io
import os
import struct
import sys
import threading
import time
from typing import TYPE_CHECKING

from ..types import snowflake
from .errors import SinkException

if TYPE_CHECKING:
    from ..voice import VoiceClient

__all__ = (
    "Filters",
    "Sink",
    "AudioData",
    "RawData",
)


if sys.platform != "win32":
    CREATE_NO_WINDOW = 0
else:
    CREATE_NO_WINDOW = 0x08000000


default_filters = {
    "time": 0,
    "users": [],
    "max_size": 0,
    "fill_silence": False,
}


class Filters:
    """Filters for :class:`~.Sink`

    .. versionadded:: 2.0

    Parameters
    ----------
    container
        Container of all Filters.
    """

    def __init__(self, **kwargs):
        self.filtered_users = kwargs.get("users", default_filters["users"])
        self.seconds = kwargs.get("time", default_filters["time"])
        self.max_size = kwargs.get("max_size", default_filters["max_size"])
        self.fill_silence = kwargs.get("fill_silence", default_filters["fill_silence"])
        self.finished = False

    @staticmethod
    def container(func):  # Contains all filters
        def _filter(self, data, user):
            if not self.filtered_users or user in self.filtered_users:
                return func(self, data, user)

        return _filter

    def init(self):
        if self.seconds != 0:
            thread = threading.Thread(target=self.wait_and_stop)
            thread.start()

    def wait_and_stop(self):
        time.sleep(self.seconds)
        if self.finished:
            return
        self.vc.stop_recording()


class RawData:
    """Handles raw data from Discord so that it can be decrypted and decoded to be used.

    .. versionadded:: 2.0
    """

    def __init__(self, data, client):
        self.data = bytearray(data)
        self.client = client

        unpacker = struct.Struct(">xxHII")
        self.sequence, self.timestamp, self.ssrc = unpacker.unpack_from(self.data[:12])

        # RFC3550 5.1: RTP Fixed Header Fields
        if self.client.mode.endswith("_rtpsize"):
            # If It Has CSRC Chunks
            cutoff = 12 + (data[0] & 0b00_0_0_1111) * 4
            # If It Has A Extension
            if data[0] & 0b00_0_1_0000:
                cutoff += 4
        else:
            cutoff = 12

        self.header = data[:cutoff]
        self.data = self.data[cutoff:]

        self.decrypted_data = getattr(self.client, f"_decrypt_{self.client.mode}")(
            self.header, self.data
        )
        self.decoded_data = None

        self.user_id = None
        self.receive_time = time.perf_counter()


class AudioData:
    """Handles data that's been completely decrypted and decoded and is ready to be saved to file.

    .. versionadded:: 2.0
    """

    def __init__(self, file):
        self.file = file
        self.finished = False

    def write(self, data):
        """Writes audio data.

        Raises
        ------
        ClientException
            The AudioData is already finished writing.
        """
        if self.finished:
            raise SinkException("The AudioData is already finished writing.")
        try:
            self.file.write(data)
        except ValueError:
            pass

    def cleanup(self):
        """Finishes and cleans up the audio data.

        Raises
        ------
        ClientException
            The AudioData is already finished writing.
        """
        if self.finished:
            raise SinkException("The AudioData is already finished writing.")
        self.file.seek(0)
        self.finished = True

    def on_format(self, encoding):
        """Called when audio data is formatted.

        Raises
        ------
        ClientException
            The AudioData is still writing.
        """
        if not self.finished:
            raise SinkException("The AudioData is still writing.")


class Sink(Filters):
    """A sink "stores" recorded audio data.

    Can be subclassed for extra customizablilty.

    .. warning::
        It is recommended you use
        the officially provided sink classes,
        such as :class:`~discord.sinks.WaveSink`.

    just replace the following like so: ::

        vc.start_recording(
            MySubClassedSink(),
            finished_callback,
            ctx.channel,
        )

    .. versionadded:: 2.0

    Raises
    ------
    ClientException
        An invalid encoding type was specified.
    ClientException
        Audio may only be formatted after recording is finished.
    """

    __sink_listeners__: list[tuple[str, str]] = []

    def __init__(self, *, filters=None):
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)
        self.vc: VoiceClient | None = None
        self.audio_data = {}
        self._last_packet_end_ts = {}
        self.parent: Sink | None = None
        self._children: list[Sink] = []

    @property
    def root(self) -> Sink:
        sink = self
        while sink.parent is not None:
            sink = sink.parent
        return sink

    @property
    def children(self) -> list[Sink]:
        return self._children

    @property
    def client(self) -> VoiceClient | None:
        return self.vc

    def init(self, vc: VoiceClient):  # called under listen
        self.vc = vc
        super().init()
        for child in self._children:
            child.init(vc)

    def add_child(self, sink: Sink) -> Sink:
        sink.parent = self
        self._children.append(sink)
        if self.vc is not None:
            sink.init(self.vc)
        return sink

    def remove_child(self, sink: Sink) -> None:
        try:
            self._children.remove(sink)
        except ValueError:
            return
        sink.parent = None

    def walk_children(self, *, with_self: bool = False):
        if with_self:
            yield self
        for child in self._children:
            yield child
            yield from child.walk_children()

    def is_opus(self) -> bool:
        return getattr(self, "encoding", "").lower() == "opus"

    def _resolve_audio_payload(self, data) -> bytes | None:
        if self.is_opus():
            opus_data = getattr(data, "opus", None)
            if isinstance(opus_data, (bytes, bytearray, memoryview)):
                return bytes(opus_data)

        pcm_data = getattr(data, "pcm", None)
        if isinstance(pcm_data, (bytes, bytearray, memoryview)):
            return bytes(pcm_data)

        if isinstance(data, (bytes, bytearray, memoryview)):
            return bytes(data)

        return None

    def _resolve_packet_timestamp(self, data):
        packet = getattr(data, "packet", None)
        if packet is None:
            return None
        ts = getattr(packet, "timestamp", None)
        if isinstance(ts, int):
            return ts
        return None

    @Filters.container
    def write(self, data, user):
        payload = self._resolve_audio_payload(data)
        if not payload:
            return

        if user not in self.audio_data:
            file = io.BytesIO()
            self.audio_data.update({user: AudioData(file)})

        file = self.audio_data[user]

        if self.fill_silence and not self.is_opus():
            ts = self._resolve_packet_timestamp(data)
            if ts is not None:
                # Opus @ 48kHz decoded PCM is 16-bit stereo: 4 bytes per sample.
                bytes_per_sample = 4
                payload_samples = len(payload) // bytes_per_sample
                prev_end_ts = self._last_packet_end_ts.get(user)
                if prev_end_ts is not None:
                    gap_samples = ts - prev_end_ts
                    if 0 < gap_samples <= 48000 * 5:
                        file.write(b"\x00" * (gap_samples * bytes_per_sample))
                if payload_samples > 0:
                    self._last_packet_end_ts[user] = ts + payload_samples

        file.write(payload)

    def cleanup(self):
        self.finished = True
        for file in self.audio_data.values():
            file.cleanup()
            self.format_audio(file)
        for child in self._children:
            child.cleanup()

    def get_all_audio(self):
        """Gets all audio files."""
        return [x.file for x in self.audio_data.values()]

    def get_user_audio(self, user: snowflake.Snowflake):
        """Gets the audio file(s) of one specific user."""
        return os.path.realpath(self.audio_data.pop(user))
