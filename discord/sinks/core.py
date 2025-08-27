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

import asyncio
from collections.abc import Callable, Coroutine
from functools import partial
import io
import os
import struct
import sys
import threading
import time
from typing import TYPE_CHECKING, Any, TypeVar, overload

from discord.utils import MISSING

from .enums import FilteringMode
from .errors import SinkException

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    from discord import abc
    from discord.types import snowflake
    from ..voice.client import VoiceClient

    R = TypeVar('R')
    P = ParamSpec('P')

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
}


class Filter:
    """Represents a filter for a :class:`~.Sink`.

    This has to be inherited in order to provide a filter to a sink.

    .. versionadded:: 2.7
    """

    @overload
    async def filter(self, sink: Sink, user: abc.Snowflake, ssrc: int, packet: RawData) -> bool: ...

    @overload
    def filter(self, sink: Sink, user: abc.Snowflake, ssrc: int, packet: RawData) -> bool: ...

    def filter(self, sink: Sink, user: abc.Snowflake, ssrc: int, packet: RawData) -> bool | Coroutine[Any, Any, bool]:
        """|maybecoro|

        Represents the filter callback.

        This is called automatically everytime a voice packet is received to check whether it should be stored in
        ``sink``.

        Parameters
        ----------
        sink: :class:`~.Sink`
            The sink the packet was received from, if the filter check goes through.
        user: :class:`~discord.abc.Snowflake`
            The user that the packet was received from.
        ssrc: :class:`int`
            The user's ssrc.
        packet: :class:`~.RawData`
            The raw data packet.

        Returns
        -------
        :class:`bool`
            Whether the filter was successful.
        """
        raise NotImplementedError('subclasses must implement this')

    def cleanup(self) -> None:
        """A function called when the filter is ready for cleanup."""
        pass


class Handler:
    """Represents a handler for a :class:`~.Sink`.

    This has to be inherited in order to provide a handler to a sink.

    .. versionadded:: 2.7
    """

    @overload
    async def handle(self, sink: Sink, user: abc.Snowflake, ssrc: int, packet: RawData) -> Any: ...

    @overload
    def handle(self, sink: Sink, user: abc.Snowflake, ssrc: int, packet: RawData) -> Any: ...

    def handle(self, sink: Sink, user: abc.Snowflake, ssrc: int, packet: RawData) -> Any | Coroutine[Any, Any, Any]:
        """|maybecoro|

        Represents the handler callback.

        This is called automatically everytime a voice packet which has successfully passed the filters is received.

        Parameters
        ----------
        sink: :class:`~.Sink`
            The sink the packet was received from, if the filter check goes through.
        user: :class:`~discord.abc.Snowflake`
            The user that the packet is from.
        ssrc: :class:`int`
            The user's ssrc.
        packet: :class:`~.RawData`
            The raw data packet.
        """
        raise NotImplementedError('subclasses must implement this')

    def cleanup(self) -> None:
        """A function called when the handler is ready for cleanup."""
        pass


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

    if TYPE_CHECKING:
        sequence: int
        timestamp: int
        ssrc: int

    def __init__(self, data: bytes, client: VoiceClient):
        self.data: bytearray = bytearray(data)
        self.client: VoiceClient = client

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

        self.header: bytes = data[:cutoff]
        self.data = self.data[cutoff:]

        self.decrypted_data: bytes = getattr(
            self.client, f"_decrypt_{self.client.mode}"
        )(self.header, self.data)
        self.decoded_data: bytes | None = None

        self.user_id: int | None = None
        self.receive_time: float = time.perf_counter()


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

    def __init__(self, *, filters=None):
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)
        self.vc: VoiceClient | None = None
        self.audio_data = {}

    def init(self, vc):  # called under listen
        self.vc = vc
        super().init()

    @Filters.container
    def write(self, data, user):
        if user not in self.audio_data:
            file = io.BytesIO()
            self.audio_data.update({user: AudioData(file)})

        file = self.audio_data[user]
        file.write(data)

    def cleanup(self):
        self.finished = True
        for file in self.audio_data.values():
            file.cleanup()
            self.format_audio(file)

    def get_all_audio(self):
        """Gets all audio files."""
        return [x.file for x in self.audio_data.values()]

    def get_user_audio(self, user: snowflake.Snowflake):
        """Gets the audio file(s) of one specific user."""
        return os.path.realpath(self.audio_data.pop(user))


class Sink:
    """Represents a sink for voice recording.

    This is used as a way of "storing" the recordings.

    This class is abstracted, and must be subclassed in order to apply functionalities to
    it.

    Parameters
    ----------
    filters: List[:class:`~.Filter`]
        The filters to apply to this sink recorder.
    filtering_mode: :class:`~.FilteringMode`
        How the filters should work. If set to :attr:`~.FilteringMode.all`, all filters must go through
        in order for an audio packet to be stored in this sink, else if it is set to :attr:`~.FilteringMode.any`,
        only one filter is required to return ``True`` in order for an audio packet to be stored in this sink.
    handlers: List[:class:`~.Handler`]
        The sink handlers. Handlers are objects that are called after filtering, and that can be used to, for example
        store a certain packet data in a file, or local mapping.
    """

    __listeners__: dict[str, list[Callable[..., Any]]] = {}

    def __init_subclass__(cls) -> None:
        listeners: dict[str, list[Callable[..., Any]]] = {}

        for base in reversed(cls.__mro__):
            for elem, value in base.__dict__.items():
                if elem in listeners:
                    del listeners[elem]

                if isinstance(value, staticmethod):
                    value = value.__func__
                elif isinstance(value, classmethod):
                    value = partial(value.__func__, cls)

                if not hasattr(value, '__listener__'):
                    continue

                event_name = getattr(value, '__listener_name__', elem).removeprefix('on_')

                try:
                    listeners[event_name].append(value)
                except KeyError:
                    listeners[event_name] = [value]

        cls.__listeners__ = listeners

    def __init__(
        self,
        *,
        filters: list[Filter] = MISSING,
        filtering_mode: FilteringMode = FilteringMode.all,
        handlers: list[Handler] = MISSING,
    ) -> None:
        self.filtering_mode: FilteringMode = filtering_mode
        self._filters: list[Filter] = filters or []
        self._handlers: list[Handler] = handlers or []
        self.__dispatch_set: set[asyncio.Task[Any]] = set()

    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> Any:
        event = event.removeprefix('on_')

        listeners = self.__listeners__.get(event, [])

        for listener in listeners:
            task = asyncio.create_task(
                listener(*args, **kwargs),
                name=f'dispatch-{event}:{id(listener):#x}',
            )
            self.__dispatch_set.add(task)
            task.add_done_callback(self.__dispatch_set.remove)

    def cleanup(self) -> None:
        """Cleans all the data in this sink.

        This should be called when you won't be performing any more operations in this sink.
        """

        for task in list(self.__dispatch_set):
            if task.done():
                continue
            task.set_result(None)

        for filter in self._filters:
            filter.cleanup()

        for handler in self._handlers:
            handler.cleanup()

    def __del__(self) -> None:
        self.cleanup()

    def add_filter(self, filter: Filter, /) -> None:
        """Adds a filter to this sink.

        Parameters
        ----------
        filter: :class:`~.Filter`
            The filter to add.

        Raises
        ------
        TypeError
            You did not provide a Filter object.
        """

        if not isinstance(filter, Filter):
            raise TypeError(f'expected a Filter object, not {filter.__class__.__name__}')
        self._filters.append(filter)

    def remove_filter(self, filter: Filter, /) -> None:
        """Removes a filter from this sink.

        Parameters
        ----------
        filter: :class:`~.Filter`
            The filter to remove.
        """

        try:
            self._filters.remove(filter)
        except ValueError:
            pass

    def add_handler(self, handler: Handler, /) -> None:
        """Adds a handler to this sink.

        Parameters
        ----------
        handler: :class:`~.Handler`
            The handler to add.

        Raises
        ------
        TypeError
            You did not provide a Handler object.
        """

        if not isinstance(handler, Handler):
            raise TypeError(f'expected a Handler object, not {handler.__class__.__name__}')
        self._handlers.append(handler)

    def remove_handler(self, handler: Handler, /) -> None:
        """Removes a handler from this sink.

        Parameters
        ----------
        handler: :class:`~.Handler`
            The handler to remove.
        """

        try:
            self._handlers.remove(handler)
        except ValueError:
            pass

    @staticmethod
    def listener(event: str = MISSING) -> Callable[[Callable[P, Coroutine[Any, Any, R]]], Callable[P, Coroutine[Any, Any, R]]]:
        """Registers a function to be an event listener for this sink.

        The events must be a :ref:`coroutine <coroutine>`, if not, :exc:`TypeError` is raised; and
        also must be inside a sink class.

        Example
        -------

        .. code-block:: python3

            class MySink(Sink):
                @Sink.listener()
                async def on_member_speaking_state_update(member, ssrc, state):
                    pass

        Parameters
        ----------
        event: :class:`str`
            The event name to listen to. If not provided, defaults to the function name.

        Raises
        ------
        TypeError
            The coroutine passed is not actually a coroutine, or the listener is not in a sink class.
        """

        def decorator(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, R]]:
            parts = func.__qualname__.split('.')

            if not parts or not len(parts) > 1:
                raise TypeError('event listeners must be declared in a Sink class')

            if parts[-1] != func.__name__:
                raise NameError('qualified name and function name mismatch, this should not happen')

            if not asyncio.iscoroutinefunction(func):
                raise TypeError('event listeners must be coroutine functions')

            func.__listener__ = True
            if event is not MISSING:
                func.__listener_name__ = event
            return func
        return decorator
