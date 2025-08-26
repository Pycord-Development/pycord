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

import logging
import select
import threading
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import VoiceClient
    from .gateway import VoiceWebSocket

SocketReaderCallback = Callable[[bytes], Any]
_log = logging.getLogger(__name__)


class SocketEventReader(threading.Thread):
    def __init__(
        self, state: VoiceConnectionState, *, start_paused: bool = True
    ) -> None:
        super().__init__(
            daemon=True,
            name=f"voice-socket-reader:{id(self):#x}",
        )
        self.state: VoiceConnectionState = state
        self.start_paused: bool = start_paused
        self._callbacks: list[SocketReaderCallback] = []
        self._running: threading.Event = threading.Event()
        self._end: threading.Event = threading.Event()
        self._idle_paused: bool = True

    def register(self, callback: SocketReaderCallback) -> None:
        self._callbacks.append(callback)
        if self._idle_paused:
            self._idle_paused = False
            self._running.set()

    def unregister(self, callback: SocketReaderCallback) -> None:
        try:
            self._callbacks.remove(callback)
        except ValueError:
            pass
        else:
            if not self._callbacks and self._running.is_set():
                self._idle_paused = True
                self._running.clear()

    def pause(self) -> None:
        self._idle_paused = False
        self._running.clear()

    def resume(self, *, force: bool = False) -> None:
        if self._running.is_set():
            return

        if not force and not self._callbacks:
            self._idle_paused = True
            return

        self._idle_paused = False
        self._running.set()

    def stop(self) -> None:
        self._end.set()
        self._running.set()

    def run(self) -> None:
        self._end.clear()
        self._running.set()

        if self.start_paused:
            self.pause()

        try:
            self._do_run()
        except Exception:
            _log.exception("Error while starting socket event reader at %s", self)
        finally:
            self.stop()
            self._running.clear()
            self._callbacks.clear()

    def _do_run(self) -> None:
        while not self._end.is_set():
            if not self._running.is_set():
                self._running.wait()
                continue

            try:
                readable, _, _ = select.select([self.state.socket], [], [], 30)
            except (ValueError, TypeError, OSError) as e:
                _log.debug(
                    "Select error handling socket in reader, this should be safe to ignore: %s: %s",
                    e.__class__.__name__,
                    e,
                )
                continue

            if not readable:
                continue

            try:
                data = self.state.socket.recv(2048)
            except OSError:
                _log.debug(
                    "Error reading from socket in %s, this should be safe to ignore.",
                    self,
                    exc_info=True,
                )
            else:
                for cb in self._callbacks:
                    try:
                        cb(data)
                    except Exception:
                        _log.exception(
                            "Error while calling %s in %s",
                            cb,
                            self,
                        )


class VoiceConnectionState:
    def __init__(
        self,
        client: VoiceClient,
        *,
        hook: (
            Callable[[VoiceWebSocket, dict[str, Any]], Coroutine[Any, Any, Any]] | None
        ) = None,
    ) -> None:
        ...
        # TODO: finish this
