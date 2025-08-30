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
import select
import socket
import struct
import threading
import time
from collections import deque
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any, TypedDict

from discord import opus, utils
from discord.backoff import ExponentialBackoff
from discord.enums import SpeakingState, try_enum
from discord.errors import ConnectionClosed
from discord.object import Object
from discord.sinks import RawData, Sink

from .enums import ConnectionFlowState, OpCodes
from .gateway import VoiceWebSocket

if TYPE_CHECKING:
    from discord import abc
    from discord.guild import Guild
    from discord.member import VoiceState
    from discord.raw_models import RawVoiceServerUpdateEvent, RawVoiceStateUpdateEvent
    from discord.state import ConnectionState
    from discord.types.voice import SupportedModes
    from discord.user import ClientUser

    from .client import VoiceClient

MISSING = utils.MISSING
SocketReaderCallback = Callable[[bytes], Any]
_log = logging.getLogger(__name__)


class SocketReader(threading.Thread):
    def __init__(
        self,
        state: VoiceConnectionState,
        name: str,
        buffer_size: int,
        *,
        start_paused: bool = True,
    ) -> None:
        super().__init__(
            daemon=True,
            name=name,
        )

        self.buffer_size: int = buffer_size
        self.state: VoiceConnectionState = state
        self.start_paused: bool = start_paused
        self._callbacks: list[SocketReaderCallback] = []
        self._running: threading.Event = threading.Event()
        self._end: threading.Event = threading.Event()
        self._idle_paused: bool = True
        self._started: threading.Event = threading.Event()

    def is_running(self) -> bool:
        return self._started.is_set()

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

    def is_paused(self) -> bool:
        return self._idle_paused or (
            not self._running.is_set() and not self._end.is_set()
        )

    def resume(self, *, force: bool = False) -> None:
        if self._running.is_set():
            return

        if not force and not self._callbacks:
            self._idle_paused = True
            return

        self._idle_paused = False
        self._running.set()

    def stop(self) -> None:
        self._started.clear()
        self._end.set()
        self._running.set()

    def run(self) -> None:
        self._started.set()
        self._end.clear()
        self._running.set()

        if self.start_paused:
            self.pause()

        try:
            self._do_run()
        except Exception:
            _log.exception(
                "An error ocurred while running the socket reader %s",
                self.name,
            )
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
                data = self.state.socket.recv(self.buffer_size)
            except OSError:
                _log.debug(
                    "Error reading from socket in %s, this should be safe to ignore",
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


class SocketVoiceRecvReader(SocketReader):
    def __init__(
        self,
        state: VoiceConnectionState,
        *,
        start_paused: bool = True,
    ) -> None:
        super().__init__(
            state,
            f"voice-recv-socket-reader:{id(self):#x}",
            4096,
            start_paused=start_paused,
        )


class SocketEventReader(SocketReader):
    def __init__(
        self, state: VoiceConnectionState, *, start_paused: bool = True
    ) -> None:
        super().__init__(
            state,
            f"voice-socket-event-reader:{id(self):#x}",
            2048,
            start_paused=start_paused,
        )


class DecoderThread(threading.Thread, opus._OpusStruct):
    def __init__(
        self,
        state: VoiceConnectionState,
        *,
        start_paused: bool = True,
    ) -> None:
        super().__init__(
            daemon=True,
            name=f"voice-recv-decoder-thread:{id(self):#x}",
        )

        self.state: VoiceConnectionState = state
        self.client: VoiceClient = state.client
        self.start_paused: bool = start_paused
        self._idle_paused: bool = True
        self._started: threading.Event = threading.Event()
        self._running: threading.Event = threading.Event()
        self._end: threading.Event = threading.Event()

        self.decode_queue: deque[RawData] = deque()
        self.decoders: dict[int, opus.Decoder] = {}

        self._end: threading.Event = threading.Event()

    def decode(self, frame: RawData) -> None:
        _log.debug('Decoding frame %s', frame)
        if not isinstance(frame, RawData):
            raise TypeError(
                f"expected a RawData object, got {frame.__class__.__name__}"
            )
        self.decode_queue.append(frame)

    def is_running(self) -> bool:
        return self._started.is_set()

    def pause(self) -> None:
        self._idle_paused = False
        self._running.clear()

    def resume(self, *, force: bool = False) -> None:
        if self._running.is_set():
            return

        if not force and not self.decode_queue:
            self._idle_paused = True
            return

        self._idle_paused = False
        self._running.set()

    def stop(self) -> None:
        self._started.clear()
        self._end.set()
        self._running.set()

    def run(self) -> None:
        self._started.set()
        self._end.clear()
        self._running.set()

        if self.start_paused:
            self.pause()

        try:
            self._do_run()
        except Exception:
            _log.exception(
                "An error ocurred while running the decoder thread %s",
                self.name,
            )
        finally:
            self.stop()
            self._running.clear()
            self.decode_queue.clear()

    def get_decoder(self, ssrc: int) -> opus.Decoder:
        try:
            return self.decoders[ssrc]
        except KeyError:
            d = self.decoders[ssrc] = opus.Decoder()
            return d

    def _do_run(self) -> None:
        while not self._end.is_set():
            if not self._running.is_set():
                self._running.wait()
                continue

            try:
                data = self.decode_queue.popleft()
            except IndexError:
                continue

            try:
                if data.decrypted_data is None:
                    continue
                else:
                    data.decoded_data = self.get_decoder(data.ssrc).decode(
                        data.decrypted_data,
                    )
            except opus.OpusError:
                _log.exception(
                    "Error ocurred while decoding opus frame",
                    exc_info=True,
                )

            self.state.dispatch_packet_sinks(data)


class SSRC(TypedDict):
    user_id: int
    speaking: SpeakingState


class VoiceConnectionState:
    def __init__(
        self,
        client: VoiceClient,
        *,
        hook: (
            Callable[[VoiceWebSocket, dict[str, Any]], Coroutine[Any, Any, Any]] | None
        ) = None,
    ) -> None:
        self.client: VoiceClient = client
        self.hook = hook
        self.loop: asyncio.AbstractEventLoop = client.loop

        self.timeout: float = 30.0
        self.reconnect: bool = True
        self.self_deaf: bool = False
        self.self_mute: bool = False
        self.endpoint: str | None = None
        self.endpoint_ip: str | None = None
        self.server_id: int | None = None
        self.ip: str | None = None
        self.port: int | None = None
        self.voice_port: int | None = None
        self.secret_key: list[int] = MISSING
        self.ssrc: int = MISSING
        self.mode: SupportedModes = MISSING
        self.socket: socket.socket = MISSING
        self.ws: VoiceWebSocket = MISSING
        self.session_id: str | None = None
        self.token: str | None = None

        self._connection: ConnectionState = client._state
        self._state: ConnectionFlowState = ConnectionFlowState.disconnected
        self._expecting_disconnect: bool = False
        self._connected = threading.Event()
        self._state_event = asyncio.Event()
        self._disconnected = asyncio.Event()
        self._runner: asyncio.Task[None] | None = None
        self._connector: asyncio.Task[None] | None = None
        self._socket_reader = SocketEventReader(self)
        self._socket_reader.start()
        self._voice_recv_socket = SocketVoiceRecvReader(self)
        self._voice_recv_socket.register(self.handle_voice_recv_packet)
        self._decoder_thread = DecoderThread(self)
        self.user_ssrc_map: dict[int, SSRC] = {}
        self.user_voice_timestamps: dict[int, tuple[int, float]] = {}
        self.sync_recording_start: bool = False
        self.first_received_packet_ts: float = MISSING
        self.sinks: list[Sink] = []
        self.recording_done_callbacks: list[
            tuple[Callable[..., Coroutine[Any, Any, Any]], tuple[Any, ...]]
        ] = []
        self.__sink_dispatch_task_set: set[asyncio.Task[Any]] = set()

    def start_record_socket(self) -> None:
        if self._voice_recv_socket.is_paused():
            self._voice_recv_socket.resume()
            return
        if self._voice_recv_socket.is_running():
            return
        self._voice_recv_socket.start()

    def stop_record_socket(self) -> None:
        if self._voice_recv_socket.is_running():
            self._voice_recv_socket.stop()

        for cb, args in self.recording_done_callbacks:
            task = self.loop.create_task(cb(*args))
            self.__sink_dispatch_task_set.add(task)
            task.add_done_callback(self.__sink_dispatch_task_set.remove)

        for sink in self.sinks:
            sink.stop()

        self.recording_done_callbacks.clear()
        self.sinks.clear()

    def handle_voice_recv_packet(self, packet: bytes) -> None:
        _log.debug('Handling voice packet %s', packet)
        if packet[1] != 0x78:
            # We should ignore any payload types we do not understand
            # Ref: RFC 3550 5.1 payload type
            # At some point we noted that we should ignore only types 200 - 204 inclusive.
            # They were marked as RTCP: provides information about the connection
            # this was too broad of a whitelist, it is unclear if this is too narrow of a whitelist
            return

        if self.paused_recording():
            return

        data = RawData(packet, self.client)

        if data.decrypted_data != opus.OPUS_SILENCE:
            return

        self._decoder_thread.decode(data)

    def is_first_packet(self) -> bool:
        return not self.user_voice_timestamps or not self.sync_recording_start

    def dispatch_packet_sinks(self, data: RawData) -> None:
        _log.debug('Dispatching packet %s in all sinks', data)
        if data.ssrc not in self.user_ssrc_map:
            if self.is_first_packet():
                self.first_received_packet_ts = data.receive_time
                silence = 0
            else:
                silence = (data.receive_time - self.first_received_packet_ts) * 48000
        else:
            stored_timestamp, stored_recv_time = self.user_voice_timestamps[data.ssrc]
            dRT = data.receive_time - stored_recv_time * 48000
            dT = data.timestamp - stored_timestamp
            diff = abs(100 - dT * 100 / dRT)

            if diff > 60 and dT != 960:
                silence = dRT - 960
            else:
                silence = dT - 960

        self.user_voice_timestamps[data.ssrc] = (data.timestamp, data.receive_time)

        data.decoded_data = (
            struct.pack("<h", 0) * max(0, int(silence)) * opus._OpusStruct.CHANNELS
            + data.decoded_data
        )

        while data.ssrc not in self.user_ssrc_map:
            time.sleep(0.05)

        task = self.loop.create_task(
            self._dispatch_packet(data),
        )
        self.__sink_dispatch_task_set.add(task)
        task.add_done_callback(self.__sink_dispatch_task_set.remove)

    async def _dispatch_packet(self, data: RawData) -> None:
        user = self.get_user_by_ssrc(data.ssrc)
        if not user:
            _log.debug(
                "Ignoring received packet %s because the SSRC was waited for but was not found",
                data,
            )
            return

        data.user_id = user.id

        for sink in self.sinks:
            if sink.is_paused():
                continue

            sink.dispatch("unfiltered_voice_packet_receive", user, data)

            if sink._filters:
                futures = [
                    self.loop.create_task(
                        utils.maybe_coroutine(fil.filter_packet, sink, user, data)
                    )
                    for fil in sink._filters
                ]
                strat = sink._filter_strat

                done, pending = await asyncio.wait(futures)

                if pending:
                    for task in pending:
                        task.set_result(False)

                    done = (*done, *pending)

                result = strat([f.result() for f in done])
            else:
                result = True

            if result:
                sink.dispatch("voice_packet_receive", user, data)
                sink._call_voice_packet_handlers(user, data)

    def is_recording(self) -> bool:
        return self._voice_recv_socket.is_running()

    def paused_recording(self) -> bool:
        return self._voice_recv_socket.is_paused()

    def add_sink(self, sink: Sink) -> None:
        self.sinks.append(sink)
        self.start_record_socket()

    def remove_sink(self, sink: Sink) -> None:
        try:
            self.sinks.remove(sink)
        except ValueError:
            pass

    def get_user_by_ssrc(self, ssrc: int) -> abc.Snowflake | None:
        data = self.user_ssrc_map.get(ssrc)
        if data is None:
            return None

        user = int(data["user_id"])
        return self.get_user(user)

    def get_user(self, id: int) -> abc.Snowflake:
        state = self._connection
        return self.guild.get_member(id) or state.get_user(id) or Object(id=id)

    def ws_hook(self, ws: VoiceWebSocket, msg: dict[str, Any]) -> None:
        op = msg["op"]
        data = msg.get("d", {})

        if op == OpCodes.speaking:
            ssrc = data["ssrc"]
            user = int(data["user_id"])
            raw_speaking = data["speaking"]
            speaking = try_enum(SpeakingState, raw_speaking)
            old_data = self.user_ssrc_map.get(ssrc)
            old_speaking = (old_data or {}).get("speaking", SpeakingState.none)

            self.dispatch_speaking_state(old_speaking, speaking, user)

            if old_data is None:
                self.user_ssrc_map[ssrc]["speaking"] = speaking
            else:
                self.user_ssrc_map[ssrc] = {
                    "user_id": user,
                    "speaking": speaking,
                }

    def dispatch_speaking_state(
        self, before: SpeakingState, after: SpeakingState, user_id: int
    ) -> None:
        task = self.loop.create_task(
            self._dispatch_speaking_state(before, after, user_id),
        )
        self.__sink_dispatch_task_set.add(task)
        task.add_done_callback(self.__sink_dispatch_task_set.remove)

    async def _dispatch_speaking_state(
        self, before: SpeakingState, after: SpeakingState, uid: int
    ) -> None:
        resolved = self.get_user(uid)

        for sink in self.sinks:
            if sink.is_paused():
                continue

            sink.dispatch("unfiltered_speaking_state_update", resolved, before, after)

            if sink._filters:
                futures = [
                    self.loop.create_task(
                        utils.maybe_coroutine(fil.filter_packet, sink, resolved, before, after)
                    )
                    for fil in sink._filters
                ]
                strat = sink._filter_strat

                done, pending = await asyncio.wait(futures)

                if pending:
                    for task in pending:
                        task.set_result(False)

                    done = (*done, *pending)

                result = strat([f.result() for f in done])
            else:
                result = True

            if result:
                sink.dispatch("speaking_state_update", resolved, before, after)
                sink._call_speaking_state_handlers(resolved, before, after)

    @property
    def state(self) -> ConnectionFlowState:
        return self._state

    @state.setter
    def state(self, state: ConnectionFlowState) -> None:
        if state is not self._state:
            _log.debug("State changed from %s to %s", self._state.name, state.name)

        self._state = state
        self._state_event.set()
        self._state_event.clear()

        if state is ConnectionFlowState.connected:
            self._connected.set()
        else:
            self._connected.clear()

    @property
    def guild(self) -> Guild:
        return self.client.guild

    @property
    def user(self) -> ClientUser:
        return self.client.user

    @property
    def channel_id(self) -> int | None:
        return self.client.channel and self.client.channel.id

    @property
    def guild_id(self) -> int:
        return self.guild.id

    @property
    def supported_modes(self) -> tuple[SupportedModes, ...]:
        return self.client.supported_modes

    @property
    def self_voice_state(self) -> VoiceState | None:
        return self.guild.me.voice

    def is_connected(self) -> bool:
        return self.state is ConnectionFlowState.connected

    def _inside_runner(self) -> bool:
        return self._runner is not None and asyncio.current_task() == self._runner

    async def voice_state_update(self, data: RawVoiceStateUpdateEvent) -> None:
        channel_id = data.channel_id

        if channel_id is None:
            self._disconnected.set()

            if self._expecting_disconnect:
                self._expecting_disconnect = False
            else:
                _log.debug("We have been disconnected from voice")
                await self.disconnect()
            return

        self.session_id = data["session_id"]

        if self.state in (
            ConnectionFlowState.set_guild_voice_state,
            ConnectionFlowState.got_voice_server_update,
        ):
            if self.state is ConnectionFlowState.set_guild_voice_state:
                self.state = ConnectionFlowState.got_voice_state_update

                if channel_id != self.client.channel.id:
                    # moved from channel
                    self._update_voice_channel(channel_id)
            else:
                self.state = ConnectionFlowState.got_both_voice_updates
            return

        if self.state is ConnectionFlowState.connected:
            self._update_voice_channel(channel_id)

        elif self.state is not ConnectionFlowState.disconnected:
            if channel_id != self.client.channel.id:
                _log.info("We were moved from the channel while connecting...")

                self._update_voice_channel(channel_id)
                await self.soft_disconnect(
                    with_state=ConnectionFlowState.got_voice_state_update
                )
                await self.connect(
                    reconnect=self.reconnect,
                    timeout=self.timeout,
                    self_deaf=(self.self_voice_state or self).self_deaf,
                    self_mute=(self.self_voice_state or self).self_mute,
                    resume=False,
                    wait=False,
                )
            else:
                _log.debug("Ignoring unexpected VOICE_STATEUPDATE event")

    async def voice_server_update(self, data: RawVoiceServerUpdateEvent) -> None:
        previous_token = self.token
        previous_server_id = self.server_id
        previous_endpoint = self.endpoint

        self.token = data.token
        self.server_id = data.guild_id
        endpoint = data.endpoint

        if self.token is None or endpoint is None:
            _log.warning(
                "Awaiting endpoint... This requires waiting. "
                "If timeout occurred considering raising the timeout and reconnecting."
            )
            return

        # strip the prefix off since we add it later
        self.endpoint = endpoint.removeprefix("wss://")

        if self.state in (
            ConnectionFlowState.set_guild_voice_state,
            ConnectionFlowState.got_voice_state_update,
        ):
            self.endpoint_ip = MISSING
            self._create_socket()

            if self.state is ConnectionFlowState.set_guild_voice_state:
                self.state = ConnectionFlowState.got_voice_server_update
            else:
                self.state = ConnectionFlowState.got_both_voice_updates

        elif self.state is ConnectionFlowState.connected:
            _log.debug("Voice server update, closing old voice websocket")
            await self.ws.close(4014)  # 4014 = main gw dropped
            self.state = ConnectionFlowState.got_voice_server_update

        elif self.state is not ConnectionFlowState.disconnected:
            if (
                previous_token == self.token
                and previous_server_id == self.server_id
                and previous_endpoint == self.endpoint
            ):
                return

            _log.debug("Unexpected VOICE_SERVER_UPDATE event received, handling...")

            await self.soft_disconnect(
                with_state=ConnectionFlowState.got_voice_server_update
            )
            await self.connect(
                reconnect=self.reconnect,
                timeout=self.timeout,
                self_deaf=(self.self_voice_state or self).self_deaf,
                self_mute=(self.self_voice_state or self).self_mute,
                resume=False,
                wait=False,
            )
            self._create_socket()

    async def connect(
        self,
        *,
        reconnect: bool,
        timeout: float,
        self_deaf: bool,
        self_mute: bool,
        resume: bool,
        wait: bool = True,
    ) -> None:
        if self._connector:
            self._connector.cancel()
            self._connector = None

        if self._runner:
            self._runner.cancel()
            self._runner = None

        self.timeout = timeout
        self.reconnect = reconnect
        self._connector = self.client.loop.create_task(
            self._wrap_connect(
                reconnect,
                timeout,
                self_deaf,
                self_mute,
                resume,
            ),
            name=f"voice-connector:{id(self):#x}",
        )

        if wait:
            await self._connector

    async def _wrap_connect(
        self,
        reconnect: bool,
        timeout: float,
        self_deaf: bool,
        self_mute: bool,
        resume: bool,
    ) -> None:
        try:
            await self._connect(reconnect, timeout, self_deaf, self_mute, resume)
        except asyncio.CancelledError:
            _log.debug("Cancelling voice connection")
            await self.soft_disconnect()
            raise
        except asyncio.TimeoutError:
            _log.info("Timed out while connecting to voice")
            await self.disconnect()
            raise
        except Exception:
            _log.exception("Error while connecting to voice... disconnecting")
            await self.disconnect()
            raise

    async def _inner_connect(
        self, reconnect: bool, self_deaf: bool, self_mute: bool, resume: bool
    ) -> None:
        for i in range(5):
            _log.info("Starting voice handshake (connection attempt %s)", i + 1)

            await self._voice_connect(self_deaf=self_deaf, self_mute=self_mute)
            if self.state is ConnectionFlowState.disconnected:
                self.state = ConnectionFlowState.set_guild_voice_state

            await self._wait_for_state(ConnectionFlowState.got_both_voice_updates)

            _log.info("Voice handshake complete. Endpoint found: %s", self.endpoint)

            try:
                self.ws = await self._connect_websocket(resume)
                await self._handshake_websocket()
                break
            except ConnectionClosed:
                if reconnect:
                    wait = 1 + i * 2
                    _log.exception(
                        "Failed to connect to voice... Retrying in %s seconds", wait
                    )
                    await self.disconnect(cleanup=False)
                    await asyncio.sleep(wait)
                    continue
                else:
                    await self.disconnect()
                    raise

    async def _connect(
        self,
        reconnect: bool,
        timeout: float,
        self_deaf: bool,
        self_mute: bool,
        resume: bool,
    ) -> None:
        _log.info(f"Connecting to voice {self.client.channel.id}")

        await asyncio.wait_for(
            self._inner_connect(
                reconnect=reconnect,
                self_deaf=self_deaf,
                self_mute=self_mute,
                resume=resume,
            ),
            timeout=timeout,
        )
        _log.info("Voice connection completed")

        if not self._runner:
            self._runner = self.client.loop.create_task(
                self._poll_ws(reconnect),
                name=f"voice-ws-poller:{id(self):#x}",
            )

    async def disconnect(
        self, *, force: bool = True, cleanup: bool = True, wait: bool = False
    ) -> None:
        if not force and not self.is_connected():
            return

        _log.debug(
            "Attempting a voice disconnect for channel %s (guild %s)",
            self.channel_id,
            self.guild_id,
        )
        try:
            await self._voice_disconnect()
            if self.ws:
                await self.ws.close()
        except Exception:
            _log.debug(
                "Ignoring exception while disconnecting from voice", exc_info=True
            )
        finally:
            self.state = ConnectionFlowState.disconnected
            self._socket_reader.pause()

            if cleanup:
                self._socket_reader.stop()
                self.stop_record_socket()
                self.client.stop()

            self._connected.set()
            self._connected.clear()

            if self.socket:
                self.socket.close()

            self.ip = MISSING
            self.port = MISSING

            if wait and not self._inside_runner():
                try:
                    await asyncio.wait_for(
                        self._disconnected.wait(), timeout=self.timeout
                    )
                except TimeoutError:
                    _log.debug("Timed out waiting for voice disconnect confirmation")
                except asyncio.CancelledError:
                    pass

            if cleanup:
                self.client.cleanup()

    async def soft_disconnect(
        self,
        *,
        with_state: ConnectionFlowState = ConnectionFlowState.got_both_voice_updates,
    ) -> None:
        _log.debug("Soft disconnecting from voice")

        if self._runner:
            self._runner.cancel()
            self._runner = None

        try:
            if self.ws:
                await self.ws.close()
        except Exception:
            _log.debug(
                "Ignoring exception while soft disconnecting from voice", exc_info=True
            )
        finally:
            self.state = with_state
            self._socket_reader.pause()
            self._voice_recv_socket.pause()

            if self.socket:
                self.socket.close()

            self.ip = MISSING
            self.port = MISSING

    async def move_to(
        self, channel: abc.Snowflake | None, timeout: float | None
    ) -> None:
        if channel is None:
            await self.disconnect(wait=True)
            return

        if self.client.channel and channel.id == self.client.channel.id:
            return

        previous_state = self.state
        await self._move_to(channel)

        last_state = self.state

        try:
            await self.wait_for(timeout=timeout)
        except asyncio.TimeoutError:
            _log.warning(
                "Timed out trying to move to channel %s in guild %s",
                channel.id,
                self.guild.id,
            )
            if self.state is last_state:
                _log.debug(
                    "Reverting state %s to previous state: %s",
                    last_state.name,
                    previous_state.name,
                )
                self.state = previous_state

    def wait_for(
        self,
        state: ConnectionFlowState = ConnectionFlowState.connected,
        timeout: float | None = None,
    ) -> Any:
        if state is ConnectionFlowState.connected:
            return self._connected.wait(timeout)
        return self._wait_for_state(state, timeout=timeout)

    def send_packet(self, packet: bytes) -> None:
        self.socket.sendall(packet)

    def add_socket_listener(self, callback: SocketReaderCallback) -> None:
        _log.debug("Registering a socket listener callback %s", callback)
        self._socket_reader.register(callback)

    def remove_socket_listener(self, callback: SocketReaderCallback) -> None:
        _log.debug("Unregistering a socket listener callback %s", callback)
        self._socket_reader.unregister(callback)

    async def _wait_for_state(
        self,
        *states: ConnectionFlowState,
        timeout: float | None = None,
    ) -> None:
        if not states:
            raise ValueError

        while True:
            if self.state in states:
                return

            _, pending = await asyncio.wait(
                [
                    asyncio.ensure_future(self._state_event.wait()),
                ],
                timeout=timeout,
            )
            if pending:
                # if we're here, it means that the state event
                # has timed out, so just raise the exception
                raise asyncio.TimeoutError

    async def _voice_connect(
        self, *, self_deaf: bool = False, self_mute: bool = False
    ) -> None:
        channel = self.client.channel
        await channel.guild.change_voice_state(
            channel=channel, self_deaf=self_deaf, self_mute=self_mute
        )

    async def _voice_disconnect(self) -> None:
        _log.info(
            "Terminating voice handshake for channel %s (guild %s)",
            self.client.channel.id,
            self.client.guild.id,
        )

        self.state = ConnectionFlowState.disconnected
        await self.client.channel.guild.change_voice_state(channel=None)
        self._expecting_disconnect = True
        self._disconnected.clear()

    async def _connect_websocket(self, resume: bool) -> VoiceWebSocket:
        seq_ack = -1
        if self.ws is not MISSING:
            seq_ack = self.ws.seq_ack
        ws = await VoiceWebSocket.from_state(
            self, resume=resume, hook=self.hook, seq_ack=seq_ack
        )
        self.state = ConnectionFlowState.websocket_connected
        return ws

    async def _handshake_websocket(self) -> None:
        while not self.ip:
            await self.ws.poll_event()

        self.state = ConnectionFlowState.got_ip_discovery
        while self.ws.secret_key is None:
            await self.ws.poll_event()

        self.state = ConnectionFlowState.connected

    def _create_socket(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(False)
        self._socket_reader.resume()

    async def _poll_ws(self, reconnect: bool) -> None:
        backoff = ExponentialBackoff()

        while True:
            try:
                await self.ws.poll_event()
            except asyncio.CancelledError:
                return
            except (ConnectionClosed, asyncio.TimeoutError) as exc:
                if isinstance(exc, ConnectionClosed):
                    # 1000 - normal closure - not resumable
                    # 4014 - externally disconnected - not resumable
                    # 4015 - voice server crashed - resumable
                    # 4021 - ratelimited, not reconnect - not resumable
                    # 4022 - call terminated, similar to 4014 - not resumable

                    if exc.code == 1000:
                        if not self._expecting_disconnect:
                            _log.info(
                                "Disconnecting from voice manually, close code %d",
                                exc.code,
                            )
                            await self.disconnect()
                        break
                    elif exc.code in (4014, 4022):
                        if self._disconnected.is_set():
                            _log.info(
                                "Disconnectinf from voice by Discord, close code %d",
                                exc.code,
                            )
                            await self.disconnect()
                            break

                        _log.info(
                            "Disconnecting from voice by force... potentially reconnecting..."
                        )
                        successful = await self._potential_reconnect()
                        if not successful:
                            _log.info(
                                "Reconnect was unsuccessful, disconnecting from voice normally"
                            )
                            if self.state is not ConnectionFlowState.disconnected:
                                await self.disconnect()
                            break
                        else:
                            # we have successfully resumed so just keep polling events
                            continue
                    elif exc.code == 4021:
                        _log.warning(
                            "We are being rate limited while attempting to connect to voice. Disconnecting...",
                        )
                        if self.state is not ConnectionFlowState.disconnected:
                            await self.disconnect()
                        break
                    elif exc.code == 4015:
                        _log.info(
                            "Disconnected from voice due to a Discord-side issue, attempting to reconnect and resume...",
                        )

                        try:
                            await self._connect(
                                reconnect=reconnect,
                                timeout=self.timeout,
                                self_deaf=(self.self_voice_state or self).self_deaf,
                                self_mute=(self.self_voice_state or self).self_mute,
                                resume=True,
                            )
                        except asyncio.TimeoutError:
                            _log.info(
                                "Could not resume the voice connection... Disconnecting..."
                            )
                            if self.state is not ConnectionFlowState.disconnected:
                                await self.disconnect()
                            break
                        except Exception:
                            _log.exception(
                                "An exception was raised while attempting a reconnect and resume... Disconnecting...",
                                exc_info=True,
                            )
                            if self.state is not ConnectionFlowState.disconnected:
                                await self.disconnect()
                            break
                        else:
                            _log.info(
                                "Successfully reconnected and resume the voice connection"
                            )
                            continue
                    else:
                        _log.debug(
                            "Not handling close code %s (%s)",
                            exc.code,
                            exc.reason or "No reason was provided",
                        )

                if not reconnect:
                    await self.disconnect()
                    raise

                retry = backoff.delay()
                _log.exception(
                    "Disconnected from voice... Reconnecting in %.2fs",
                    retry,
                )
                await asyncio.sleep(retry)
                await self.disconnect(cleanup=False)

                try:
                    await self._connect(
                        reconnect=reconnect,
                        timeout=self.timeout,
                        self_deaf=(self.self_voice_state or self).self_deaf,
                        self_mute=(self.self_voice_state or self).self_mute,
                        resume=False,
                    )
                except asyncio.TimeoutError:
                    _log.warning("Could not connect to voice... Retrying...")
                    continue

    async def _potential_reconnect(self) -> bool:
        try:
            await self._wait_for_state(
                ConnectionFlowState.got_voice_server_update,
                ConnectionFlowState.got_both_voice_updates,
                ConnectionFlowState.disconnected,
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            return False
        else:
            if self.state is ConnectionFlowState.disconnected:
                return False

        previous_ws = self.ws

        try:
            self.ws = await self._connect_websocket(False)
            await self._handshake_websocket()
        except (ConnectionClosed, asyncio.TimeoutError):
            return False
        else:
            return True
        finally:
            await previous_ws.close()

    async def _move_to(self, channel: abc.Snowflake) -> None:
        await self.client.channel.guild.change_voice_state(channel=channel)
        self.state = ConnectionFlowState.set_guild_voice_state

    def _update_voice_channel(self, channel_id: int | None) -> None:
        self.client.channel = channel_id and self.guild.get_channel(channel_id)  # type: ignore
