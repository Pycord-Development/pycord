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

from collections import deque
from collections.abc import Callable
import threading
import logging
from typing import TYPE_CHECKING, Any
import queue

from discord.opus import PacketDecoder

from ..utils.multidataevent import MultiDataEvent

if TYPE_CHECKING:
    from discord.sinks import Sink

    from .reader import AudioReader
    from ..packets import RTPPacket, RTCPPacket

    EventCB = Callable[..., Any]
    EventData = tuple[str, tuple[Any, ...], dict[str, Any]]

_log = logging.getLogger(__name__)


class PacketRouter(threading.Thread):
    def __init__(self, sink: Sink, reader: AudioReader) -> None:
        super().__init__(
            daemon=True,
            name=f'voice-receiver-packet-router:{id(self):#x}',
        )

        self.sink: Sink = sink
        self.decoders: dict[int, PacketDecoder] = {}
        self.reader: AudioReader = reader
        self.waiter: MultiDataEvent[PacketDecoder] = MultiDataEvent()

        self._lock: threading.RLock = threading.RLock()
        self._end_thread: threading.Event = threading.Event()
        self._dropped_ssrcs: deque[int] = deque(maxlen=16)

    def feed_rtp(self, packet: RTPPacket) -> None:
        if packet.ssrc in self._dropped_ssrcs:
            _log.debug("Ignoring packet from dropped ssrc %s", packet.ssrc)

        with self._lock:
            decoder = self.get_decoder(packet.ssrc)
            if decoder is not None:
                decoder.push_packet(packet)

    def feed_rtcp(self, packet: RTCPPacket) -> None:
        guild = self.sink.client.guild if self.sink.client else None
        event_router = self.reader.event_router
        event_router.dispatch('rtcp_packet', packet, guild)

    def get_decoder(self, ssrc: int) -> PacketDecoder | None:
        with self._lock:
            decoder = self.decoders.get(ssrc)
            if decoder is None:
                decoder = self.decoders[ssrc] = PacketDecoder(self, ssrc)
            return decoder

    def set_sink(self, sink: Sink) -> None:
        with self._lock:
            self.sink = sink

    def set_user_id(self, ssrc: int, user_id: int) -> None:
        with self._lock:
            if ssrc in self._dropped_ssrcs:
                self._dropped_ssrcs.remove(ssrc)

            decoder = self.decoders.get(ssrc)
            if decoder is not None:
                decoder.set_user_id(user_id)

    def destroy_decoder(self, ssrc: int) -> None:
        with self._lock:
            decoder = self.decoders.pop(ssrc, None)
            if decoder is not None:
                self._dropped_ssrcs.append(ssrc)
                decoder.destroy()

    def destroy_all_decoders(self) -> None:
        with self._lock:
            for ssrc in self.decoders.keys():
                self.destroy_decoder(ssrc)

    def stop(self) -> None:
        self._end_thread.set()
        self.waiter.notify()

    def run(self) -> None:
        try:
            self._do_run()
        except Exception as exc:
            _log.exception("Error in %s loop", self)
            self.reader.error = exc
        finally:
            self.reader.client.stop_recording()
            self.waiter.clear()

    def _do_run(self) -> None:
        while not self._end_thread.is_set():
            self.waiter.wait()

            with self._lock:
                for decoder in self.waiter.items:
                    data = decoder.pop_data()
                    if data is not None:
                        self.sink.write(data.source, data)


class SinkEventRouter(threading.Thread):
    def __init__(self, sink: Sink, reader: AudioReader) -> None:
        super().__init__(daemon=True, name=f"voice-receiver-sink-event-router:{id(self):#x}")

        self.sink: Sink = sink
        self.reader: AudioReader = reader

        self._event_listeners: dict[str, list[EventCB]] = {}
        self._buffer: queue.SimpleQueue[EventData] = queue.SimpleQueue()
        self._lock = threading.RLock()
        self._end_thread = threading.Event()

        self.register_events()

    def dispatch(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        _log.debug("Dispatch voice event %s", event)
        self._buffer.put_nowait((event, args, kwargs))

    def set_sink(self, sink: Sink) -> None:
        with self._lock:
            self.unregister_events()
            self.sink = sink
            self.register_events()

    def register_events(self) -> None:
        with self._lock:
            self._register_listeners(self.sink)
            for child in self.sink.walk_children():
                self._register_listeners(child)

    def unregister_events(self) -> None:
        with self._lock:
            self._unregister_listeners(self.sink)
            for child in self.sink.walk_children():
                self._unregister_listeners(child)

    def _register_listeners(self, sink: Sink) -> None:
        _log.debug("Registering events for %s: %s", sink, sink.__sink_listeners__)

        for name, method_name in sink.__sink_listeners__:
            func = getattr(sink, method_name)
            _log.debug("Registering event: %r (callback at %r)", name, method_name)

            if name in self._event_listeners:
                self._event_listeners[name].append(func)
            else:
                self._event_listeners[name] = [func]

    def _unregister_listeners(self, sink: Sink) -> None:
        for name, method_name in sink.__sink_listeners__:
            func = getattr(sink, method_name)

            if name in self._event_listeners:
                try:
                    self._event_listeners[name].remove(func)
                except ValueError:
                    pass

    def _dispatch_to_listeners(self, event: str, *args: Any, **kwargs: Any) -> None:
        for listener in self._event_listeners.get(f"on_{event}", []):
            try:
                listener(*args, **kwargs)
            except Exception as exc:
                _log.exception("Unhandled exception while dispatching event %s (args: %s; kwargs: %s)", event, args, kwargs, exc_info=exc)

    def stop(self) -> None:
        self._end_thread.set()

    def run(self) -> None:
        try:
            self._do_run()
        except Exception as exc:
            _log.exception("Error in sink event router", exc_info=exc)
            self.reader.error = exc
            self.reader.client.stop_listening()

    def _do_run(self) -> None:
        while not self._end_thread.is_set():
            try:
                event, args, kwargs = self._buffer.get(timeout=0.5)
            except queue.Empty:
                continue
            else:
                with self._lock:
                    with self.reader.packet_router._lock:
                        self._dispatch_to_listeners(event, *args, **kwargs)
