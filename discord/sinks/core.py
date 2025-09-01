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
import logging
import struct
import sys
import time
from collections import namedtuple
from collections.abc import Callable, Coroutine, Iterable
from functools import partial
from typing import TYPE_CHECKING, Any, Generic, TypeVar, overload

from discord import opus, utils
from discord.enums import SpeakingState
from discord.utils import MISSING

from .enums import SinkFilteringMode

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    from discord import abc

    from ..voice.client import VoiceClient

    R = TypeVar("R")
    P = ParamSpec("P")

__all__ = (
    "Sink",
    "RawData",
    "SinkFilter",
    "SinkHandler",
)


if sys.platform != "win32":
    CREATE_NO_WINDOW = 0
else:
    CREATE_NO_WINDOW = 0x08000000


S = TypeVar("S", bound="Sink")
_log = logging.getLogger(__name__)


def is_rtcp(data: bytes) -> bool:
    return 200 <= data[1] <= 204


class SinkFilter(Generic[S]):
    """Represents a filter for a :class:`~.Sink`.

    This has to be inherited in order to provide a filter to a sink.

    .. versionadded:: 2.7
    """

    @overload
    async def filter_packet(
        self, sink: S, user: abc.Snowflake, packet: RawData
    ) -> bool: ...

    @overload
    def filter_packet(self, sink: S, user: abc.Snowflake, packet: RawData) -> bool: ...

    def filter_packet(
        self, sink: S, user: abc.Snowflake, packet: RawData
    ) -> bool | Coroutine[Any, Any, bool]:
        """|maybecoro|

        This is called automatically everytime a voice packet is received.

        Depending on what bool-like this returns, it will dispatch some events in the parent ``sink``.

        Parameters
        ----------
        sink: :class:`~.Sink`
            The sink the packet was received from, if the filter check goes through.
        user: :class:`~discord.abc.Snowflake`
            The user that the packet was received from.
        packet: :class:`~.RawData`
            The raw data packet.

        Returns
        -------
        :class:`bool`
            Whether the filter was successful.
        """
        raise NotImplementedError("subclasses must implement this")

    @overload
    async def filter_speaking_state(
        self, sink: S, user: abc.Snowflake, before: SpeakingState, after: SpeakingState
    ) -> bool: ...

    @overload
    def filter_speaking_state(
        self, sink: S, user: abc.Snowflake, before: SpeakingState, after: SpeakingState
    ) -> bool: ...

    def filter_speaking_state(
        self, sink: S, user: abc.Snowflake, before: SpeakingState, after: SpeakingState
    ) -> bool | Coroutine[Any, Any, bool]:
        """|maybecoro|

        This is called automatically everytime a speaking state is updated.

        Depending on what bool-like this returns, it will dispatch some events in the parent ``sink``.

        Parameters
        ----------
        sink: :class:`~.Sink`
            The sink the packet was received from, if the filter check goes through.
        user: :class:`~discord.abc.Snowflake`
            The user that the packet was received from.
        before: :class:`~discord.SpeakingState`
            The speaking state before the update.
        after: :class:`~discord.SpeakingState`
            The speaking state after the update.

        Returns
        -------
        :class:`bool`
            Whether the filter was successful.
        """
        raise NotImplementedError("subclasses must implement this")

    @overload
    async def filter_user_connect(
        self,
        sink: S,
        user: abc.Snowflake,
        channel: abc.Snowflake,
    ) -> bool: ...

    @overload
    def filter_user_connect(
        self,
        sink: S,
        user: abc.Snowflake,
        channel: abc.Snowflake,
    ) -> bool: ...

    def filter_user_connect(
        self,
        sink: S,
        user: abc.Snowflake,
        channel: abc.Snowflake,
    ) -> bool | Coroutine[Any, Any, bool]:
        """|maybecoro|

        This is called automatically everytime a speaking state is updated.

        Depending on what bool-like this returns, it will dispatch some events in the parent ``sink``.

        Parameters
        ----------
        sink: :class:`~.Sink`
            The sink the packet was received from, if the filter check goes through.
        user: :class:`~discord.abc.Snowflake`
            The user that the packet was received from.
        channel: :class:`~discord.abc.Snowflake`
            The channel the user has connected to. This is usually resolved into the proper guild channel type, but
            defaults to a :class:`~discord.Object` when not found.

        Returns
        -------
        :class:`bool`
            Whether the filter was successful.
        """
        raise NotImplementedError("subclasses must implement this")

    def cleanup(self) -> None:
        """A function called when the filter is ready for cleanup."""


class SinkHandler(Generic[S]):
    """Represents a handler for a :class:`~.Sink`.

    This has to be inherited in order to provide a handler to a sink.

    .. versionadded:: 2.7
    """

    @overload
    async def handle_packet(
        self, sink: S, user: abc.Snowflake, packet: RawData
    ) -> Any: ...

    @overload
    def handle_packet(self, sink: S, user: abc.Snowflake, packet: RawData) -> Any: ...

    def handle_packet(
        self, sink: S, user: abc.Snowflake, packet: RawData
    ) -> Any | Coroutine[Any, Any, Any]:
        """|maybecoro|

        This is called automatically everytime a voice packet which has successfully passed the filters is received.

        Parameters
        ----------
        sink: :class:`~.Sink`
            The sink the packet was received from, if the filter check goes through.
        user: :class:`~discord.abc.Snowflake`
            The user that the packet is from.
        packet: :class:`~.RawData`
            The raw data packet.
        """

    @overload
    async def handle_speaking_state(
        self, sink: S, user: abc.Snowflake, before: SpeakingState, after: SpeakingState
    ) -> Any: ...

    @overload
    def handle_speaking_state(
        self, sink: S, user: abc.Snowflake, before: SpeakingState, after: SpeakingState
    ) -> Any: ...

    def handle_speaking_state(
        self, sink: S, user: abc.Snowflake, before: SpeakingState, after: SpeakingState
    ) -> Any | Coroutine[Any, Any, Any]:
        """|maybecoro|

        This is called automatically everytime a speaking state update is received which has successfully passed the filters.

        Parameters
        ----------
        sink: :class:`~.Sink`
            The sink the packet was received from, if the filter check goes through.
        user: :class:`~discord.abc.Snowflake`
            The user that the packet was received from.
        before: :class:`~discord.SpeakingState`
            The speaking state before the update.
        after: :class:`~discord.SpeakingState`
            The speaking state after the update.
        """

    @overload
    async def handle_user_connect(
        self,
        sink: S,
        user: abc.Snowflake,
        channel: abc.Snowflake,
    ) -> Any: ...

    @overload
    def handle_user_connect(
        self,
        sink: S,
        user: abc.Snowflake,
        channel: abc.Snowflake,
    ) -> Any: ...

    def handle_user_connect(
        self,
        sink: S,
        user: abc.Snowflake,
        channel: abc.Snowflake,
    ) -> Any | Coroutine[Any, Any, Any]:
        """|maybecoro|

        This is called automatically everytime a user has connected a voice channel which has successfully passed the filters.

        Parameters
        ----------
        sink: :class:`~.Sink`
            The sink the packet was received from, if the filter check goes through.
        user: :class:`~discord.abc.Snowflake`
            The user that the packet was received from.
        channel: :class:`~discord.abc.Snowflake`
            The channel the user has connected to. This is usually resolved into the proper guild channel type, but
            defaults to a :class:`~discord.Object` when not found.
        """

    def cleanup(self) -> None:
        """A function called when the handler is ready for cleanup."""


class RawData:
    """Handles raw data from Discord so that it can be decrypted and decoded to be used.

    .. versionadded:: 2.0
    """

    unpacker = struct.Struct(">xxHII")
    _ext_header = namedtuple("Extension", "profile length values")
    _ext_magic = b"\xbe\xde"

    if TYPE_CHECKING:
        sequence: int
        timestamp: int
        ssrc: int

    def __init__(self, raw_data: bytes, client: VoiceClient):
        data: bytearray = bytearray(raw_data)
        self.client: VoiceClient = client

        self.version: int = data[0] >> 6
        self.padding: bool = bool(data[0] & 0b00100000)
        self.extended: bool = bool(data[0] & 0b00010000)
        self.cc: int = data[0] & 0b00001111
        self.marker: bool = bool(data[1] & 0b10000000)
        self.payload: int = data[1] & 0b01111111

        self.sequence, self.timestamp, self.ssrc = self.unpacker.unpack_from(data)
        self.csrcs: tuple[int, ...] = ()
        self.extension = None
        self.extension_data: dict[int, bytes] = {}

        self.header = data[:12]
        self.data = data[12:]
        self.decrypted_data: bytes | None = None
        self.decoded_data: bytes = MISSING

        self.nonce: bytes = b""
        self._rtpsize: bool = False

        self._decoder: opus.Decoder = opus.Decoder()
        self.receive_time: float = time.perf_counter()

        if self.cc:
            fmt = ">%sI" % self.cc
            offset = struct.calcsize(fmt) + 12
            self.csrcs = struct.unpack(fmt, data[12:offset])
            self.data = data[offset:]

    def adjust_rtpsize(self) -> None:
        self._rtpsize = True
        self.nonce = self.data[-4:]

        if not self.extended:
            self.data = self.data[:-4]

        self.header += self.data[:4]
        self.data = self.data[4:-4]

    def update_headers(self, data: bytes) -> int:
        if not self.extended:
            return 0

        if self._rtpsize:
            data = self.header[-4:] + data

        profile, length = struct.unpack_from(">2sH", data)

        if profile == self._ext_magic:
            self._parse_bede_header(data, length)

        values = struct.unpack(">%sI" % length, data[4 : 4 + length * 4])
        self.extension = self._ext_header(profile, length, values)

        offset = 4 + length * 4
        if self._rtpsize:
            offset -= 4
        return offset

    def _parse_bede_header(self, data: bytes, length: int) -> None:
        offset = 4
        n = 0

        while n < length:
            next_byte = data[offset : offset + 1]

            if next_byte == b"\x00":
                offset += 1
                continue

            header = struct.unpack(">B", next_byte)[0]

            element_id = header >> 4
            element_len = 1 + (header & 0b0000_1111)

            self.extension_data[element_id] = data[
                offset + 1 : offset + 1 + element_len
            ]
            offset += 1 + element_len
            n += 1

    async def decode(self) -> bytes:
        if not self.decrypted_data:
            _log.debug("Attempted to decode an empty decrypted data frame")
            return b""

        return await asyncio.to_thread(
            self._decoder.decode,
            self.decrypted_data,
        )


class Sink:
    r"""Represents a sink for voice recording.

    This is used as a way of "storing" the recordings.

    This class is abstracted, and must be subclassed in order to apply functionalities to
    it.

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

    if TYPE_CHECKING:
        __filtering_mode: SinkFilteringMode
        _filter_strat: Callable[..., bool]
        client: VoiceClient

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

                if not hasattr(value, "__listener__"):
                    continue

                event_name = getattr(value, "__listener_name__", elem).removeprefix(
                    "on_"
                )

                try:
                    listeners[event_name].append(value)
                except KeyError:
                    listeners[event_name] = [value]

        cls.__listeners__ = listeners

    def __init__(
        self,
        *,
        filters: list[SinkFilter] = MISSING,
        filtering_mode: SinkFilteringMode = SinkFilteringMode.all,
        handlers: list[SinkHandler] = MISSING,
    ) -> None:
        self._paused: bool = False
        self.filtering_mode = filtering_mode
        self._filters: list[SinkFilter] = filters or []
        self._handlers: list[SinkHandler] = handlers or []
        self.__dispatch_set: set[asyncio.Task[Any]] = set()
        self._listeners: dict[str, list[Callable[[Iterable[object]], bool]]] = (
            self.__listeners__
        )

    @property
    def filtering_mode(self) -> SinkFilteringMode:
        return self.__filtering_mode

    @filtering_mode.setter
    def filtering_mode(self, value: SinkFilteringMode) -> None:
        if value is SinkFilteringMode.all:
            self._filter_strat = all
        elif value is SinkFilteringMode.any:
            self._filter_strat = any
        else:
            raise TypeError(
                f"expected a FilteringMode enum member, got {value.__class__.__name__}"
            )

        self.__filtering_mode = value

    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> Any:
        _log.debug("Dispatching sink %s event %s", self.__class__.__name__, event)
        method = f"on_{event}"

        listeners = self.__listeners__.get(event, [])
        for coro in listeners:
            self._schedule_event(coro, method, *args, **kwargs)

        try:
            coro = getattr(self, method)
        except AttributeError:
            pass
        else:
            self._schedule_event(coro, method, *args, **kwargs)

    async def _run_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            try:
                await self.on_error(event_name, exc, *args, **kwargs)
            except asyncio.CancelledError:
                pass

    def _call_voice_packet_handlers(self, user: abc.Snowflake, packet: RawData) -> None:
        for handler in self._handlers:
            task = asyncio.create_task(
                utils.maybe_coroutine(
                    handler.handle_packet,
                    self,
                    user,
                    packet,
                )
            )
            self.__dispatch_set.add(task)
            task.add_done_callback(self.__dispatch_set.discard)

    def _call_user_connect_handlers(
        self,
        user: abc.Snowflake,
        channel: abc.Snowflake,
    ) -> None:
        for handler in self._handlers:
            task = asyncio.create_task(
                utils.maybe_coroutine(
                    handler.handle_user_connect,
                    self,
                    user,
                    channel,
                ),
            )
            self.__dispatch_set.add(task)
            task.add_done_callback(self.__dispatch_set.discard)

    def _call_speaking_state_handlers(
        self, user: abc.Snowflake, before: SpeakingState, after: SpeakingState
    ) -> None:
        for handler in self._handlers:
            task = asyncio.create_task(
                utils.maybe_coroutine(
                    handler.handle_speaking_state,
                    self,
                    user,
                    before,
                    after,
                ),
            )
            self.__dispatch_set.add(task)
            task.add_done_callback(self.__dispatch_set.discard)

    def _schedule_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> asyncio.Task:
        wrapped = self._run_event(coro, event_name, *args, **kwargs)

        task = asyncio.create_task(wrapped, name=f"sinks: {event_name}")
        self.__dispatch_set.add(task)
        task.add_done_callback(self.__dispatch_set.discard)
        return task

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={id(self):#x}>"

    def stop(self) -> None:
        """Stops this sink's recording.

        This is the place where :meth:`.cleanup` should be called.
        """
        self.cleanup()

    def cleanup(self) -> None:
        """Cleans all the data in this sink.

        This should be called when you won't be performing any more operations in this sink.
        """

        for task in list(self.__dispatch_set):
            if task.done():
                continue
            task.cancel()

        for filter in self._filters:
            filter.cleanup()

        for handler in self._handlers:
            handler.cleanup()

    def add_filter(self, filter: SinkFilter, /) -> None:
        """Adds a filter to this sink.

        Parameters
        ----------
        filter: :class:`~.SinkFilter`
            The filter to add.

        Raises
        ------
        TypeError
            You did not provide a Filter object.
        """

        if not isinstance(filter, SinkFilter):
            raise TypeError(
                f"expected a Filter object, not {filter.__class__.__name__}"
            )
        self._filters.append(filter)

    def remove_filter(self, filter: SinkFilter, /) -> None:
        """Removes a filter from this sink.

        Parameters
        ----------
        filter: :class:`~.SinkFilter`
            The filter to remove.
        """

        try:
            self._filters.remove(filter)
        except ValueError:
            pass

    def add_handler(self, handler: SinkHandler, /) -> None:
        """Adds a handler to this sink.

        Parameters
        ----------
        handler: :class:`~.SinkHandler`
            The handler to add.

        Raises
        ------
        TypeError
            You did not provide a Handler object.
        """

        if not isinstance(handler, SinkHandler):
            raise TypeError(
                f"expected a Handler object, not {handler.__class__.__name__}"
            )
        self._handlers.append(handler)

    def remove_handler(self, handler: SinkHandler, /) -> None:
        """Removes a handler from this sink.

        Parameters
        ----------
        handler: :class:`~.SinkHandler`
            The handler to remove.
        """

        try:
            self._handlers.remove(handler)
        except ValueError:
            pass

    @staticmethod
    def listener(
        event: str = MISSING,
    ) -> Callable[
        [Callable[P, Coroutine[Any, Any, R]]], Callable[P, Coroutine[Any, Any, R]]
    ]:
        """Registers a function to be an event listener for this sink.

        The events must be a :ref:`coroutine <coroutine>`, if not, :exc:`TypeError` is raised; and
        also must be inside a sink class.

        Parameters
        ----------
        event: :class:`str`
            The event name to listen to. If not provided, defaults to the function name.

        Raises
        ------
        TypeError
            The coroutine passed is not actually a coroutine, or the listener is not in a sink class.

        Example
        -------

        .. code-block:: python3

            class MySink(Sink):
                @Sink.listener()
                async def on_member_speaking_state_update(member, ssrc, state):
                    pass
        """

        def decorator(
            func: Callable[P, Coroutine[Any, Any, R]],
        ) -> Callable[P, Coroutine[Any, Any, R]]:
            parts = func.__qualname__.split(".")

            if not parts or not len(parts) > 1:
                raise TypeError("event listeners must be declared in a Sink class")

            if parts[-1] != func.__name__:
                raise NameError(
                    "qualified name and function name mismatch, this should not happen"
                )

            if not asyncio.iscoroutinefunction(func):
                raise TypeError("event listeners must be coroutine functions")

            func.__listener__ = True
            if event is not MISSING:
                func.__listener_name__ = event
            return func

        return decorator

    async def on_voice_packet_receive(self, user: abc.Snowflake, data: RawData) -> None:
        pass

    async def on_unfiltered_voice_packet_receive(
        self, user: abc.Snowflake, data: RawData
    ) -> None:
        pass

    async def on_speaking_state_update(
        self, user: abc.Snowflake, before: SpeakingState, after: SpeakingState
    ) -> None:
        pass

    async def on_unfiltered_speaking_state_update(
        self, user: abc.Snowflake, before: SpeakingState, after: SpeakingState
    ) -> None:
        pass

    async def on_user_connect(
        self,
        user: abc.Snowflake,
        channel: abc.Snowflake,
    ) -> None:
        pass

    async def on_unfiltered_user_connect(
        self, user: abc.Snowflake, channel: abc.Snowflake
    ) -> None:
        pass

    async def on_error(
        self, event: str, exception: Exception, *args: Any, **kwargs: Any
    ) -> None:
        _log.exception(
            "An error ocurred in sink %s while dispatching the event %s",
            self,
            event,
            exc_info=exception,
        )

    def is_recording(self) -> bool:
        """Whether this sink is currently available to record, and doing so."""
        state = self.client._connection
        return state.is_recording() and id(self) in state._sinks

    def is_paused(self) -> bool:
        """Whether this sink is currently paused from recording."""
        return self._paused

    def pause(self) -> None:
        """Pauses the recording of this sink.

        No filter or handlers will be called when a sink is paused, and no
        event will be dispatched.

        Pending events _could still be called_ even when a sink is paused,
        so make sure you pause a sink when there are not current packets being
        handled.

        You can resume the recording of this sink with :meth:`.resume`.
        """
        self._paused = True

    def resume(self) -> None:
        """Resumes the recording of this sink.

        You can pause the recording of this sink with :meth:`.pause`.
        """
        self._paused = False
