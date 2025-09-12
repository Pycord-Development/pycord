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
import threading
import time
from collections import deque
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any

import aiohttp
import davey

from discord import utils
from discord.enums import SpeakingState
from discord.errors import ConnectionClosed
from discord.gateway import DiscordWebSocket
from discord.gateway import KeepAliveHandler as KeepAliveHandlerBase

from .enums import OpCodes

if TYPE_CHECKING:
    from _typeshed import ConvertibleToInt
    from typing_extensions import Self

    from .state import VoiceConnectionState

_log = logging.getLogger(__name__)


class KeepAliveHandler(KeepAliveHandlerBase):
    if TYPE_CHECKING:
        ws: VoiceWebSocket

    def __init__(
        self,
        *args: Any,
        ws: VoiceWebSocket,
        interval: float | None = None,
        **kwargs: Any,
    ) -> None:
        daemon: bool = kwargs.pop("daemon", True)
        name: str = kwargs.pop("name", f"voice-keep-alive-handler:{id(self):#x}")
        super().__init__(
            *args,
            **kwargs,
            name=name,
            daemon=daemon,
            ws=ws,
            interval=interval,
        )

        self.msg: str = "Keeping shard ID %s voice websocket alive with timestamp %s."
        self.block_msg: str = (
            "Shard ID %s voice heartbeat blocked for more than %s seconds."
        )
        self.behing_msg: str = (
            "High socket latency, shard ID %s heartbeat is %.1fs behind."
        )
        self.recent_ack_latencies: deque[float] = deque(maxlen=20)

    def get_payload(self) -> dict[str, Any]:
        return {
            "op": int(OpCodes.heartbeat),
            "d": {
                "t": int(time.time() * 1000),
                "seq_ack": self.ws.seq_ack,
            },
        }

    def ack(self) -> None:
        ack_time = time.perf_counter()
        self._last_ack = ack_time
        self._last_recv = ack_time
        self.latency = ack_time - self._last_send
        self.recent_ack_latencies.append(self.latency)


class VoiceWebSocket(DiscordWebSocket):
    def __init__(
        self,
        socket: aiohttp.ClientWebSocketResponse,
        loop: asyncio.AbstractEventLoop,
        state: VoiceConnectionState,
        *,
        hook: Callable[..., Coroutine[Any, Any, Any]] | None = None,
    ) -> None:
        self.ws: aiohttp.ClientWebSocketResponse = socket
        self.loop: asyncio.AbstractEventLoop = loop
        self._keep_alive: KeepAliveHandler | None = None
        self._close_code: int | None = None
        self.secret_key: list[int] | None = None
        self.seq_ack: int = -1
        self.state: VoiceConnectionState = state
        self.ssrc_map: dict[str, dict[str, Any]] = {}
        self.known_users: dict[int, Any] = {}

        if hook:
            self._hook = hook or state.ws_hook  # type: ignore

    @property
    def token(self) -> str | None:
        return self.state.token

    @token.setter
    def token(self, value: str | None) -> None:
        self.state.token = value

    @property
    def session_id(self) -> str | None:
        return self.state.session_id

    @session_id.setter
    def session_id(self, value: str | None) -> None:
        self.state.session_id = value

    @property
    def self_id(self) -> int:
        return self._connection.self_id

    async def _hook(self, *args: Any) -> Any:
        pass

    async def send_as_bytes(self, op: ConvertibleToInt, data: bytes) -> None:
        packet = bytes([int(op)]) + data
        _log.debug(
            "Sending voice websocket binary frame: op: %s size: %d", op, len(data)
        )
        await self.ws.send_bytes(packet)

    async def send_as_json(self, data: Any) -> None:
        _log.debug("Sending voice websocket frame: %s.", data)
        if data.get("op", None) == OpCodes.identify:
            _log.info("Identifying ourselves: %s", data)
        await self.ws.send_str(utils._to_json(data))

    send_heartbeat = send_as_json

    async def resume(self) -> None:
        payload = {
            "op": int(OpCodes.resume),
            "d": {
                "token": self.token,
                "server_id": str(self.state.server_id),
                "session_id": self.session_id,
                "seq_ack": self.seq_ack,
            },
        }
        await self.send_as_json(payload)

    async def received_message(self, msg: Any, /):
        _log.debug("Voice websocket frame received: %s", msg)
        op = msg["op"]
        data = msg.get("d", {})  # this key should ALWAYS be given, but guard anyways
        self.seq_ack = msg.get("seq", self.seq_ack)  # keep the seq_ack updated
        state = self.state

        if op == OpCodes.ready:
            await self.ready(data)
        elif op == OpCodes.heartbeat_ack:
            if not self._keep_alive:
                _log.error(
                    "Received a heartbeat ACK but no keep alive handler was set.",
                )
                return
            self._keep_alive.ack()
        elif op == OpCodes.resumed:
            _log.info(
                f"Voice connection on channel ID {self.state.channel_id} (guild {self.state.guild_id}) was "
                "successfully RESUMED.",
            )
        elif op == OpCodes.session_description:
            state.mode = data["mode"]
            state.dave_protocol_version = data["dave_protocol_version"]
            await self.load_secret_key(data)
            await state.reinit_dave_session()
        elif op == OpCodes.hello:
            interval = data["heartbeat_interval"] / 1000.0
            self._keep_alive = KeepAliveHandler(
                ws=self,
                interval=min(interval, 5),
            )
            self._keep_alive.start()
        elif state.dave_session:
            if op == OpCodes.dave_prepare_transition:
                _log.info(
                    "Preparing to upgrade to a DAVE connection for channel %s for transition %d proto version %d",
                    state.channel_id,
                    data["transition_id"],
                    data["protocol_version"],
                )
                state.dave_pending_transition = data

                transition_id = data["transition_id"]

                if transition_id == 0:
                    await state.execute_dave_transition(data["transition_id"])
                else:
                    if data["protocol_version"] == 0 and state.dave_session:
                        state.dave_session.set_passthrough_mode(True, 120)
                    await self.send_dave_transition_ready(transition_id)
            elif op == OpCodes.dave_execute_transition:
                _log.info(
                    "Upgrading to DAVE connection for channel %s", state.channel_id
                )
                await state.execute_dave_transition(data["transition_id"])
            elif op == OpCodes.dave_prepare_epoch:
                epoch = data["epoch"]
                _log.debug(
                    "Preparing for DAVE epoch in channel %s: %s",
                    state.channel_id,
                    epoch,
                )
                # if epoch is 1 then a new MLS group is to be created for the proto version
                if epoch == 1:
                    state.dave_protocol_version = data["protocol_version"]
                    await state.reinit_dave_session()
        else:
            _log.debug("Unhandled op code: %s with data %s", op, data)

        await utils.maybe_coroutine(self._hook, self, msg)

    async def received_binary_message(self, msg: bytes) -> None:
        self.seq_ack = struct.unpack_from(">H", msg, 0)[0]
        op = msg[2]
        _log.debug(
            "Voice websocket binary frame received: %d bytes, seq: %s, op: %s",
            len(msg),
            self.seq_ack,
            op,
        )

        state = self.state

        if not state.dave_session:
            return

        if op == OpCodes.mls_external_sender_package:
            state.dave_session.set_external_sender(msg[3:])
        elif op == OpCodes.mls_proposals:
            op_type = msg[3]
            result = state.dave_session.process_proposals(
                (
                    davey.ProposalsOperationType.append
                    if op_type == 0
                    else davey.ProposalsOperationType.revoke
                ),
                msg[4:],
            )

            if isinstance(result, davey.CommitWelcome):
                data = (
                    (result.commit + result.welcome)
                    if result.welcome
                    else result.commit
                )
                _log.debug("Sending MLS key package with data: %s", data)
                await self.send_as_bytes(
                    OpCodes.mls_commit_welcome,
                    data,
                )
            _log.debug("Processed MLS proposals for current dave session: %r", result)
        elif op == OpCodes.mls_commit_transition:
            transt_id = struct.unpack_from(">H", msg, 3)[0]
            try:
                state.dave_session.process_commit(msg[5:])
                if transt_id != 0:
                    state.dave_pending_transition = {
                        "transition_id": transt_id,
                        "protocol_version": state.dave_protocol_version,
                    }
                    _log.debug(
                        "Sending DAVE transition ready from MLS commit transition with data: %s",
                        state.dave_pending_transition,
                    )
                    await self.send_dave_transition_ready(transt_id)
                _log.debug("Processed MLS commit for transition %s", transt_id)
            except Exception as exc:
                _log.debug(
                    "An exception ocurred while processing a MLS commit, this should be safe to ignore: %s",
                    exc,
                )
                await state.recover_dave_from_invalid_commit(transt_id)
        elif op == OpCodes.mls_welcome:
            transt_id = struct.unpack_from(">H", msg, 3)[0]
            try:
                state.dave_session.process_welcome(msg[5:])
                if transt_id != 0:
                    state.dave_pending_transition = {
                        "transition_id": transt_id,
                        "protocol_version": state.dave_protocol_version,
                    }
                    _log.debug(
                        "Sending DAVE transition ready from MLS welcome with data: %s",
                        state.dave_pending_transition,
                    )
                    await self.send_dave_transition_ready(transt_id)
                _log.debug("Processed MLS welcome for transition %s", transt_id)
            except Exception as exc:
                _log.debug(
                    "An exception ocurred while processing a MLS welcome, this should be safe to ignore: %s",
                    exc,
                )
                await state.recover_dave_from_invalid_commit(transt_id)

    async def ready(self, data: dict[str, Any]) -> None:
        state = self.state

        state.ssrc = data["ssrc"]
        state.voice_port = data["port"]
        state.endpoint_ip = data["ip"]

        _log.debug(
            f"Connecting to {state.endpoint_ip} (port {state.voice_port}).",
        )

        await self.loop.sock_connect(
            state.socket,
            (state.endpoint_ip, state.voice_port),
        )

        _log.debug(
            "Connected socket to %s (port %s)",
            state.endpoint_ip,
            state.voice_port,
        )

        state.ip, state.port = await self.get_ip()

        modes = [mode for mode in data["modes"] if mode in self.state.supported_modes]
        _log.debug("Received available voice connection modes: %s", modes)

        mode = modes[0]
        await self.select_protocol(state.ip, state.port, mode)
        _log.debug("Selected voice protocol %s for this connection", mode)

    async def select_protocol(self, ip: str, port: int, mode: str) -> None:
        payload = {
            "op": int(OpCodes.select_protocol),
            "d": {
                "protocol": "udp",
                "data": {
                    "address": ip,
                    "port": port,
                    "mode": mode,
                },
            },
        }
        await self.send_as_json(payload)

    async def get_ip(self) -> tuple[str, int]:
        state = self.state
        packet = bytearray(74)
        struct.pack_into(">H", packet, 0, 1)  # 1 = Send
        struct.pack_into(">H", packet, 2, 70)  # 70 = Length
        struct.pack_into(">I", packet, 4, state.ssrc)

        _log.debug(
            f"Sending IP discovery packet for voice in channel {state.channel_id} (guild {state.guild_id})"
        )
        await self.loop.sock_sendall(state.socket, packet)

        fut: asyncio.Future[bytes] = self.loop.create_future()

        def get_ip_packet(data: bytes) -> None:
            if data[1] == 0x02 and len(data) == 74:
                self.loop.call_soon_threadsafe(fut.set_result, data)

        fut.add_done_callback(lambda f: state.remove_socket_listener(get_ip_packet))
        state.add_socket_listener(get_ip_packet)
        recv = await fut

        _log.debug("Received IP discovery packet with data %s", recv)

        ip_start = 8
        ip_end = recv.index(0, ip_start)
        ip = recv[ip_start:ip_end].decode("ascii")
        port = struct.unpack_from(">H", recv, len(recv) - 2)[0]
        _log.debug("Detected IP %s with port %s", ip, port)

        return ip, port

    @property
    def latency(self) -> float:
        heartbeat = self._keep_alive
        return float("inf") if heartbeat is None else heartbeat.latency

    @property
    def average_latency(self) -> float:
        heartbeat = self._keep_alive
        if heartbeat is None or not heartbeat.recent_ack_latencies:
            return float("inf")
        return sum(heartbeat.recent_ack_latencies) / len(heartbeat.recent_ack_latencies)

    async def load_secret_key(self, data: dict[str, Any]) -> None:
        _log.debug(
            f"Received secret key for voice connection in channel {self.state.channel_id} (guild {self.state.guild_id})"
        )
        self.secret_key = self.state.secret_key = data["secret_key"]
        await self.speak(SpeakingState.none)

    async def poll_event(self) -> None:
        msg = await asyncio.wait_for(self.ws.receive(), timeout=30)

        if msg.type is aiohttp.WSMsgType.TEXT:
            _log.debug("Received text payload: %s", msg.data)
            await self.received_message(utils._from_json(msg.data))
        elif msg.type is aiohttp.WSMsgType.BINARY:
            _log.debug("Received binary payload: size: %d", len(msg.data))
            await self.received_binary_message(msg.data)
        elif msg.type is aiohttp.WSMsgType.ERROR:
            _log.debug("Received %s", msg)
            raise ConnectionClosed(self.ws, shard_id=None) from msg.data
        elif msg.type in (
            aiohttp.WSMsgType.CLOSED,
            aiohttp.WSMsgType.CLOSE,
            aiohttp.WSMsgType.CLOSING,
        ):
            _log.debug("Received %s", msg)
            raise ConnectionClosed(self.ws, shard_id=None, code=self._close_code)

    async def close(self, code: int = 1000) -> None:
        if self._keep_alive:
            self._keep_alive.stop()

        self._close_code = code
        await self.ws.close(code=self._close_code)

    async def speak(self, state: SpeakingState = SpeakingState.voice) -> None:
        await self.send_as_json(
            {
                "op": int(OpCodes.speaking),
                "d": {
                    "speaking": int(state),
                    "delay": 0,
                },
            },
        )

    @classmethod
    async def from_state(
        cls,
        state: VoiceConnectionState,
        *,
        resume: bool = False,
        hook: Callable[..., Coroutine[Any, Any, Any]] | None = None,
        seq_ack: int = -1,
    ) -> Self:
        gateway = f"wss://{state.endpoint}/?v=8"
        client = state.client
        http = client._state.http
        socket = await http.ws_connect(gateway, compress=15)
        ws = cls(socket, loop=client.loop, hook=hook, state=state)
        ws.gateway = gateway
        ws.seq_ack = seq_ack
        ws._max_heartbeat_timeout = 60.0
        ws.thread_id = threading.get_ident()

        if resume:
            await ws.resume()
        else:
            await ws.identify()
        return ws

    async def identify(self) -> None:
        state = self.state
        payload = {
            "op": int(OpCodes.identify),
            "d": {
                "server_id": str(state.server_id),
                "user_id": str(state.user.id),
                "session_id": self.session_id,
                "token": self.token,
                "max_dave_protocol_version": state.max_dave_proto_version,
            },
        }
        await self.send_as_json(payload)

    async def send_dave_transition_ready(self, transition_id: int) -> None:
        payload = {
            "op": int(OpCodes.dave_transition_ready),
            "d": {
                "transition_id": transition_id,
            },
        }
        await self.send_as_json(payload)
