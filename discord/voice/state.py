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
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any, TypedDict

from discord import opus, utils
from discord.backoff import ExponentialBackoff
from discord.enums import SpeakingState, try_enum
from discord.errors import ConnectionClosed
from discord.object import Object
from discord.sinks import RawData, Sink

try:
    import davey
except ImportError:
    import warnings

    warnings.warn_explicit()

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
_recv_log = logging.getLogger("discord.voice.receiver")
DAVE_PROTOCOL_VERSION = davey.DAVE_PROTOCOL_VERSION


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
        self._warned_wait: bool = False

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
            self._started.clear()
            self._running.clear()
            self._callbacks.clear()

    def _do_run(self) -> None:
        while not self._end.is_set():
            if not self._running.is_set():
                if not self._warned_wait:
                    _log.warning(
                        "Socket reader %s is waiting to be set as running", self.name
                    )
                    self._warned_wait = True
                self._running.wait()
                continue

            if self._warned_wait:
                _log.info("Socket reader %s was set as running", self.name)
                self._warned_wait = False

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
                        task = asyncio.ensure_future(
                            self.state.loop.create_task(
                                utils.maybe_coroutine(cb, data)
                            ),
                            loop=self.state.loop,
                        )
                        self.state._dispatch_task_set.add(task)
                        task.add_done_callback(
                            self.state._dispatch_task_set.discard
                        )
                    except Exception:
                        _log.exception(
                            "Error while calling %s in %s",
                            cb,
                            self,
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
        self.recording_done_callbacks: list[
            tuple[Callable[..., Coroutine[Any, Any, Any]], tuple[Any, ...]]
        ] = []
        self._dispatch_task_set: set[asyncio.Task] = set()

        if not self._connection.self_id:
            raise RuntimeError("client self ID is not set")
        if not self.channel_id:
            raise RuntimeError("client channel being connected to is not set")

        self.dave_session: davey.DaveSession | None = None
        self.dave_protocol_version: int = 0
        self.dave_pending_transition: dict[str, int] | None = None
        self.downgraded_dave = False

    @property
    def user_ssrc_map(self) -> dict[int, int]:
        return self.client._id_to_ssrc

    @property
    def max_dave_proto_version(self) -> int:
        return davey.DAVE_PROTOCOL_VERSION

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

    async def reinit_dave_session(self) -> None:
        if self.dave_protocol_version > 0:
            if self.dave_session:
                self.dave_session.reinit(self.dave_protocol_version, self.user.id, self.channel_id)
            else:
                self.dave_session = davey.DaveSession(
                    self.dave_protocol_version,
                    self.user.id,
                    self.channel_id,
                )

            await self.ws.send_as_bytes(
                OpCodes.mls_key_package,
                self.dave_session.get_serialized_key_package(),
            )
        elif self.dave_session:
            self.dave_session.reset()
            self.dave_session.set_passthrough_mode(True, 10)

    async def recover_dave_from_invalid_commit(self, transition: int) -> None:
        payload = {
            "op": int(OpCodes.mls_invalid_commit_welcome),
            "d": {"transition_id": transition},
        }
        await self.ws.send_as_json(payload)
        await self.reinit_dave_session()

    async def execute_dave_transition(self, transition: int) -> None:
        _log.debug("Executing DAVE transition with id %s", transition)

        if not self.dave_pending_transition:
            _log.warning(
                "Attempted to execute a transition without having a pending transition for id %s, "
                "this is a Discord bug.",
                transition,
            )
            return

        pending_transition = self.dave_pending_transition["transition_id"]
        pending_proto = self.dave_pending_transition["protocol_version"]

        session = self.dave_session

        if transition == pending_transition:
            old_version = self.dave_protocol_version
            self.dave_protocol_version = pending_proto

            if old_version != self.dave_protocol_version and self.dave_protocol_version == 0:
                _log.warning("DAVE was downgraded, voice client non-e2ee session has been deprecated since 2.7")
                self.downgraded_dave = True
            elif transition > 0 and self.downgraded_dave:
                self.downgraded_dave = False
                if session:
                    session.set_passthrough_mode(True, 10)
                _log.info("Upgraded voice session to use DAVE")
        else:
            _log.debug(
                "Received an execute transition id %s when expected was %s, ignoring",
                transition,
                pending_proto,
            )

        self.dave_pending_transition = None
