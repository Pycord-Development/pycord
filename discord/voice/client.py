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
import datetime
import logging
import struct
from typing import TYPE_CHECKING, Any, Literal, overload
import warnings

from discord import opus
from discord.enums import SpeakingState, try_enum
from discord.errors import ClientException
from discord.player import AudioPlayer, AudioSource
from discord.sinks.core import Sink
from discord.sinks.errors import RecordingException
from discord.utils import MISSING

from ._types import VoiceProtocol
from .receive import AudioReader
from .state import VoiceConnectionState
from .enums import OpCodes

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    from discord import abc
    from discord.client import Client
    from discord.guild import Guild, VocalGuildChannel
    from discord.opus import APPLICATION_CTL, BAND_CTL, SIGNAL_CTL, Encoder
    from discord.raw_models import (
        RawVoiceServerUpdateEvent,
        RawVoiceStateUpdateEvent,
    )
    from discord.state import ConnectionState
    from discord.types.voice import SupportedModes
    from discord.user import ClientUser, User
    from discord.member import Member

    from .gateway import VoiceWebSocket
    from .receive.reader import AfterCallback

    P = ParamSpec("P")

_log = logging.getLogger(__name__)

has_nacl: bool

try:
    import nacl.secret
    import nacl.utils

    has_nacl = True
except ImportError:
    has_nacl = False

__all__ = (
    "VoiceClient",
)


class VoiceClient(VoiceProtocol):
    """Represents a Discord voice connection.

    You do not create these, you typically get them from e.g.
    :meth:`VoiceChannel.connect`.

    Attributes
    ----------
    session_id: :class:`str`
        The voice connection session ID.
    token: :class:`str`
        The voice connection token.
    endpoint: :class:`str`
        The endpoint we are connecting to.
    channel: Union[:class:`VoiceChannel`, :class:`StageChannel`]
        The channel we are connected to.

    Warning
    -------
    In order to use PCM based AudioSources, you must have the opus library
    installed on your system and loaded through :func:`opus.load_opus`.
    Otherwise, your AudioSources must be opus encoded (e.g. using :class:`FFmpegOpusAudio`)
    or the library will not be able ot transmit audio.
    """

    channel: VocalGuildChannel

    def __init__(
        self,
        client: Client,
        channel: abc.Connectable,
    ) -> None:
        if not has_nacl:
            raise RuntimeError(
                "PyNaCl library is needed in order to use voice related features, "
                'you can run "pip install py-cord[voice]" to install all voice-related '
                "dependencies."
            )

        super().__init__(client, channel)
        state = client._connection

        self.server_id: int = MISSING
        self.socket = MISSING
        self.loop: asyncio.AbstractEventLoop = state.loop
        self._state: ConnectionState = state

        self.sequence: int = 0
        self.timestamp: int = 0
        self._player: AudioPlayer | None = None
        self._player_future: asyncio.Future[None] | None = None
        self.encoder: Encoder = MISSING
        self._incr_nonce: int = 0

        self._connection: VoiceConnectionState = self.create_connection_state()

        self._ssrc_to_id: dict[int, int] = {}
        self._id_to_ssrc: dict[int, int] = {}
        self._event_listeners: dict[str, list] = {}
        self._reader: AudioReader = MISSING

    warn_nacl: bool = not has_nacl
    supported_modes: tuple[SupportedModes, ...] = (
        "aead_xchacha20_poly1305_rtpsize",
        "xsalsa20_poly1305_lite",
        "xsalsa20_poly1305_suffix",
        "xsalsa20_poly1305",
    )

    @property
    def guild(self) -> Guild:
        """Returns the guild the channel we're connecting to is bound to."""
        return self.channel.guild

    @property
    def user(self) -> ClientUser:
        """The user connected to voice (i.e. ourselves)"""
        return self._state.user  # type: ignore

    @property
    def session_id(self) -> str | None:
        return self._connection.session_id

    @property
    def token(self) -> str | None:
        return self._connection.token

    @property
    def endpoint(self) -> str | None:
        return self._connection.endpoint

    @property
    def ssrc(self) -> int:
        return self._connection.ssrc

    @property
    def mode(self) -> SupportedModes:
        return self._connection.mode

    @property
    def secret_key(self) -> list[int]:
        return self._connection.secret_key

    @property
    def ws(self) -> VoiceWebSocket:
        return self._connection.ws

    @property
    def timeout(self) -> float:
        return self._connection.timeout

    def checked_add(self, attr: str, value: int, limit: int) -> None:
        val = getattr(self, attr)
        if val + value > limit:
            setattr(self, attr, 0)
        else:
            setattr(self, attr, val + value)

    def create_connection_state(self) -> VoiceConnectionState:
        return VoiceConnectionState(self, hook=self._recv_hook)

    async def _recv_hook(self, ws: VoiceWebSocket, msg: dict[str, Any]) -> None:
        op = msg["op"]
        data = msg.get("d", {})

        if op == OpCodes.ready:
            self._add_ssrc(self.guild.me.id, data["ssrc"])
        elif op == OpCodes.speaking:
            uid = int(data["user_id"])
            ssrc = data["ssrc"]

            self._add_ssrc(uid, ssrc)

            member = self.guild.get_member(uid)
            state = try_enum(SpeakingState, data["speaking"])
            self.dispatch("member_speaking_state_update", member, ssrc, state)
        elif op == OpCodes.clients_connect:
            uids = list(map(int, data["user_ids"]))

            for uid in uids:
                member = self.guild.get_member(uid)
                if not member:
                    _log.warning("Skipping member referencing ID %d on member_connect", uid)
                    continue
                self.dispatch("member_connect", member)
        elif op == OpCodes.client_disconnect:
            uid = int(data["user_id"])
            ssrc = self._id_to_ssrc.get(uid)

            if self._reader and ssrc is not None:
                _log.debug("Destroying decoder for user %d, ssrc=%d", uid, ssrc)
                self._reader.packet_router.destroy_decoder(ssrc)

            self._remove_ssrc(user_id=uid)
            member = self.guild.get_member(uid)
            self.dispatch("member_disconnect", member, ssrc)

        # maybe handle video and such things?

    async def _run_event(self, coro, event_name: str, *args: Any, **kwargs: Any) -> None:
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception:
            _log.exception("Error calling %s", event_name)

    def _schedule_event(self, coro, event_name: str, *args: Any, **kwargs: Any) -> asyncio.Task:
        wrapped = self._run_event(coro, event_name, *args, **kwargs)
        return self.client.loop.create_task(wrapped, name=f"voice-receiver-event-dispatch: {event_name}")

    def dispatch(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        _log.debug("Dispatching voice_client event %s", event)

        event_name = f"on_{event}"
        for coro in self._event_listeners.get(event_name, []):
            task = self._schedule_event(coro, event_name, *args, **kwargs)
            self._connection._dispatch_task_set.add(task)
            task.add_done_callback(self._connection._dispatch_task_set.discard)

        self._dispatch_sink(event, *args, **kwargs)
        self.client.dispatch(event, *args, **kwargs)

    async def on_voice_state_update(self, data: RawVoiceStateUpdateEvent) -> None:
        old_channel_id = self.channel.id if self.channel else None
        await self._connection.voice_state_update(data)

        if data.channel_id is None:
            return

        if self._reader and data.channel_id != old_channel_id:
            _log.debug("Destroying voice receive decoders in guild %s", self.guild.id)
            self._reader.packet_router.destroy_all_decoders()

    async def on_voice_server_update(self, data: RawVoiceServerUpdateEvent) -> None:
        await self._connection.voice_server_update(data)

    def _dispatch_sink(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        if self._reader:
            self._reader.event_router.dispatch(event, *args, **kwargs)

    def _add_ssrc(self, user_id: int, ssrc: int) -> None:
        self._ssrc_to_id[ssrc] = user_id
        self._id_to_ssrc[user_id] = ssrc

        if self._reader:
            self._reader.packet_router.set_user_id(ssrc, user_id)

    def _remove_ssrc(self, *, user_id: int) -> None:
        ssrc = self._id_to_ssrc.pop(user_id, None)

        if ssrc:
            self._reader.speaking_timer.drop_ssrc(ssrc)
            self._ssrc_to_id.pop(ssrc, None)

    async def connect(
        self,
        *,
        reconnect: bool,
        timeout: float,
        self_deaf: bool = False,
        self_mute: bool = False,
    ) -> None:
        await self._connection.connect(
            reconnect=reconnect,
            timeout=timeout,
            self_deaf=self_deaf,
            self_mute=self_mute,
            resume=False,
        )

    def wait_until_connected(self, timeout: float | None = 30.0) -> bool:
        self._connection.wait_for(timeout=timeout)
        return self._connection.is_connected()

    @property
    def latency(self) -> float:
        """Latency between a HEARTBEAT and a HEARBEAT_ACK in seconds.

        This chould be referred to as the Discord Voice WebSocket latency and is
        and analogue of user's voice latencies as seen in the Discord client.

        .. versionadded:: 1.4
        """
        ws = self.ws
        return float("inf") if not ws else ws.latency

    @property
    def average_latency(self) -> float:
        """Average of most recent 20 HEARBEAT latencies in seconds.

        .. versionadded:: 1.4
        """
        ws = self.ws
        return float("inf") if not ws else ws.average_latency

    @property
    def privacy_code(self) -> str | None:
        """Returns the current voice session's privacy code, only available if the call has upgraded to use the
        DAVE protocol
        """
        session = self._connection.dave_session
        return session and session.voice_privacy_code

    async def disconnect(self, *, force: bool = False) -> None:
        """|coro|

        Disconnects this voice client from voice.
        """

        self.stop()
        await self._connection.disconnect(force=force, wait=True)
        self.cleanup()

    async def move_to(
        self, channel: abc.Snowflake | None, *, timeout: float | None = 30.0
    ) -> None:
        """|coro|

        moves you to a different voice channel.

        Parameters
        ----------
        channel: Optional[:class:`abc.Snowflake`]
            The channel to move to. If this is ``None``, it is an equivalent of calling :meth:`.disconnect`.
        timeout: Optional[:class:`float`]
            The maximum time in seconds to wait for the channel move to be completed, defaults to 30.
            If it is ``None``, then there is no timeout.

        Raises
        ------
        asyncio.TimeoutError
            Waiting for channel move timed out.
        """
        await self._connection.move_to(channel, timeout)

    def is_connected(self) -> bool:
        """Whether the voice client is connected to voice."""
        return self._connection.is_connected()

    def is_playing(self) -> bool:
        """INdicates if we're playing audio."""
        return self._player is not None and self._player.is_playing()

    def is_paused(self) -> bool:
        """Indicates if we're playing audio, but if we're paused."""
        return self._player is not None and self._player.is_paused()

    # audio related

    def _get_voice_packet(self, data: Any) -> bytes:

        session = self._connection.dave_session
        packet = session.encrypt_opus(data) if session and session.ready else data

        header = bytearray(12)

        # formulate rtp header
        header[0] = 0x80
        header[1] = 0x78
        struct.pack_into(">H", header, 2, self.sequence)
        struct.pack_into(">I", header, 4, self.timestamp)
        struct.pack_into(">I", header, 8, self.ssrc)

        encrypt_packet = getattr(self, f"_encrypt_{self.mode}")
        return encrypt_packet(header, packet)

    # encryption methods

    def _encrypt_xsalsa20_poly1305(self, header: bytes, data: Any) -> bytes:
        # deprecated
        box = nacl.secret.SecretBox(bytes(self.secret_key))
        nonce = bytearray(24)
        nonce[:12] = header
        return header + box.encrypt(bytes(data), bytes(nonce)).ciphertext

    def _encrypt_xsalsa20_poly1305_suffix(self, header: bytes, data: Any) -> bytes:
        # deprecated
        box = nacl.secret.SecretBox(bytes(self.secret_key))
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
        return header + box.encrypt(bytes(data), nonce).ciphertext + nonce

    def _encrypt_xsalsa20_poly1305_lite(self, header: bytes, data: Any) -> bytes:
        # deprecated
        box = nacl.secret.SecretBox(bytes(self.secret_key))
        nonce = bytearray(24)
        nonce[:4] = struct.pack(">I", self._incr_nonce)
        self.checked_add("_incr_nonce", 1, 4294967295)

        return header + box.encrypt(bytes(data), bytes(nonce)).ciphertext + nonce[:4]

    def _encrypt_aead_xchacha20_poly1305_rtpsize(
        self, header: bytes, data: Any
    ) -> bytes:
        box = nacl.secret.Aead(bytes(self.secret_key))
        nonce = bytearray(24)
        nonce[:4] = struct.pack(">I", self._incr_nonce)
        self.checked_add("_incr_nonce", 1, 4294967295)
        return (
            header
            + box.encrypt(bytes(data), bytes(header), bytes(nonce)).ciphertext
            + nonce[:4]
        )

    @overload
    def play(
        self,
        source: AudioSource,
        *,
        after: AfterCallback | None = ...,
        application: APPLICATION_CTL = ...,
        bitrate: int = ...,
        fec: bool = ...,
        expected_packet_loss: float = ...,
        bandwidth: BAND_CTL = ...,
        signal_type: SIGNAL_CTL = ...,
        wait_finish: Literal[False] = ...,
    ) -> None: ...

    @overload
    def play(
        self,
        source: AudioSource,
        *,
        after: AfterCallback = ...,
        application: APPLICATION_CTL = ...,
        bitrate: int = ...,
        fec: bool = ...,
        expected_packet_loss: float = ...,
        bandwidth: BAND_CTL = ...,
        signal_type: SIGNAL_CTL = ...,
        wait_finish: Literal[True],
    ) -> asyncio.Future[None]: ...

    def play(
        self,
        source: AudioSource,
        *,
        after: AfterCallback | None = None,
        application: APPLICATION_CTL = "audio",
        bitrate: int = 128,
        fec: bool = True,
        expected_packet_loss: float = 0.15,
        bandwidth: BAND_CTL = "full",
        signal_type: SIGNAL_CTL = "auto",
        wait_finish: bool = False,
    ) -> None | asyncio.Future[None]:
        """Plays an :class:`AudioSource`.

        The finalizer, ``after`` is called after the source has been exhausted
        or an error occurred.

        IF an error happens while the audio player is running, the exception is
        caught and the audio player is then stopped. If no after callback is passed,
        any caught exception will be displayed as if it were raised.

        Parameters
        ----------
        source: :class:`AudioSource`
            The audio source we're reading from.
        after: Callable[[Optional[:class:`Exception`]], Any]
            The finalizer that is called after the stream is exhausted.
            This function must have a single parameter, ``error``, that
            denotes an optional exception that was raised during playing.
        application: :class:`str`
            The intended application encoder application type. Must be one of
            ``audio``, ``voip``, or ``lowdelay``. Defaults to ``audio``.
        bitrate: :class:`int`
            The encoder's bitrate. Must be between ``16`` and ``512``. Defaults
            to ``128``.
        fec: :class:`bool`
            Configures the encoder's use of inband forward error correction (fec).
            Defaults to ``True``.
        expected_packet_loss: :class:`float`
            How much packet loss percentage is expected from the encoder. This requires ``fec``
            to be set to ``True``. Defaults to ``0.15``.
        bandwidth: :class:`str`
            The encoder's bandpass. Must be one of ``narrow``, ``medium``, ``wide``,
            ``superwide``, or ``full``. Defaults to ``full``.
        signal_type: :class:`str`
            The type of signal being encoded. Must be one of ``auto``, ``voice``, ``music``.
            Defaults to ``auto``.
        wait_finish: :class:`bool`
            If ``True``, then an awaitable is returned that waits for the audio source to be
            exhausted, and will return an optional exception that could have been raised.

            If ``False``, ``None`` is returned and the function does not block.

            .. versionadded:: 2.5

        Raises
        ------
        ClientException
            Already playing audio, or not connected to voice.
        TypeError
            Source is not a :class:`AudioSource`, or after is not a callable.
        OpusNotLoaded
            Source is not opus encoded and opus is not loaded.
        """

        if not self.is_connected():
            raise ClientException("Not connected to voice")
        if self.is_playing():
            raise ClientException("Already playing audio")
        if not isinstance(source, AudioSource):
            raise TypeError(
                f"Source must be an AudioSource, not {source.__class__.__name__}",
            )
        if not self.encoder and not source.is_opus():
            self.encoder = opus.Encoder(
                application=application,
                bitrate=bitrate,
                fec=fec,
                expected_packet_loss=expected_packet_loss,
                bandwidth=bandwidth,
                signal_type=signal_type,
            )

        future = None
        if wait_finish:
            self._player_future = future = self.loop.create_future()
            after_callback = after

            def _after(exc: Exception | None) -> None:
                if callable(after_callback):
                    after_callback(exc)
                future.set_result(exc)

            after = _after

        self._player = AudioPlayer(source, self, after=after)
        self._player.start()
        return future

    def stop(self) -> None:
        """Stops playing audio, if applicable."""
        if self._player:
            self._player.stop()
        if self._player_future:
            for cb, _ in self._player_future._callbacks:
                self._player_future.remove_done_callback(cb)
            self._player_future.set_result(None)
        if self._reader:
            self._reader.stop()
            self._reader = MISSING

        self._player = None
        self._player_future = None

    def pause(self) -> None:
        """Pauses the audio playing."""
        if self._player:
            self._player.pause()

    def resume(self) -> None:
        """Resumes the audio playing."""
        if self._player:
            self._player.resume()

    @property
    def source(self) -> AudioSource | None:
        """The audio source being player, if playing.

        This property can also be used to change the audio source currently being played.
        """
        return self._player and self._player.source

    @source.setter
    def source(self, value: AudioSource) -> None:
        if not isinstance(value, AudioSource):
            raise TypeError(f"expected AudioSource, not {value.__class__.__name__}")

        if self._player is None:
            raise ValueError("the client is not playing anything")

        self._player.set_source(value)

    def send_audio_packet(self, data: bytes, *, encode: bool = True) -> None:
        """Sends an audio packet composed of the ``data``.

        You must be connected to play audio.

        Parameters
        ----------
        data: :class:`bytes`
            The :term:`py:bytes-like object` denoting PCM or Opus voice data.
        encode: :class:`bool`
            Indicates if ``data`` should be encoded into Opus.

        Raises
        ------
        ClientException
            You are not connected.
        opus.OpusError
            Encoding the data failed.
        """

        self.checked_add("sequence", 1, 65535)
        if encode:
            encoded = self.encoder.encode(data, self.encoder.SAMPLES_PER_FRAME)
        else:
            encoded = data

        packet = self._get_voice_packet(encoded)
        try:
            self._connection.send_packet(packet)
        except OSError:
            _log.debug(
                "A packet has been dropped (seq: %s, timestamp: %s)",
                self.sequence,
                self.timestamp,
            )

        self.checked_add("timestamp", opus.Encoder.SAMPLES_PER_FRAME, 4294967295)

    def elapsed(self) -> datetime.timedelta:
        """Returns the elapsed time of the playing audio."""
        if self._player:
            return datetime.timedelta(milliseconds=self._player.played_frames() * 20)
        return datetime.timedelta()

    def start_recording(
        self,
        sink: Sink,
        callback: AfterCallback | None = None,
        *args: Any,
        sync_start: bool = MISSING,
    ) -> None:
        r"""Start recording the audio from the current connected channel to the provided sink.

        .. versionadded:: 2.0
        .. versionchanged:: 2.7
            You can now have multiple concurrent recording sinks in the same voice client.

        Parameters
        ----------
        sink: :class:`~.Sink`
            A Sink in which all audio packets will be processed in.
        callback: Callable[[:class:`Exception` | None], Any]
            A function which is called after the bot has stopped recording. This must take exactly one positonal(-only)
            parameter, ``exception``, which is the exception that was raised during the recording of the Sink.

            .. versionchanged:: 2.7
                This parameter is now optional, and must take exactly one parameter, ``exception``.
        \*args:
            The arguments to pass to the callback coroutine.

            .. deprecated:: 2.7
                Passing custom arguments to the callback is now deprecated and ignored.
        sync_start: :class:`bool`
            If ``True``, the recordings of subsequent users will start with silence.
            This is useful for recording audio just as it was heard.

            .. deprecated:: 2.7
                This parameter is now ignored and deprecated.

        Raises
        ------
        RecordingException
            Not connected to a voice channel
        TypeError
            You did not provide a Sink object.
        """

        if not self.is_connected():
            raise RecordingException("not connected to a voice channel")
        if not isinstance(sink, Sink):
            raise TypeError(f"expected a Sink object, got {sink.__class__.__name__}")

        if self.is_recording():
            raise ClientException("Already recording audio")

        if len(args) > 0:
            warnings.warn("'args' parameter is deprecated since 2.7 and will be removed in 3.0")
        if sync_start is not MISSING:
            warnings.warn("'sync_tart' parameter is deprecated since 2.7 and will be removed in 3.0")

        self._reader = AudioReader(sink, self, after=callback)
        self._reader.start()

    def stop_recording(self) -> None:
        """Stops the recording of the provided ``sink``, or all recording sinks.

        .. versionadded:: 2.0

        Raises
        ------
        RecordingException
            You are not recording.
        """
        if self._reader:
            self._reader.stop()
            self._reader = MISSING
        else:
            raise RecordingException("You are not recording")

    def is_recording(self) -> bool:
        """Whether the current client is recording in any sink."""
        return self._reader and self._reader.is_listening()

    def is_speaking(self, member: Member | User) -> bool | None:
        """Whether a user is speaking.

        This is an approximate calculation and may have outdated or wrong data.

        If the member speaking status has not been yet saved, it returns ``None``.

        .. versionadded:: 2.7
        """
        ssrc = self._id_to_ssrc.get(member.id)
        if ssrc is None:
            return None
        if self._reader:
            return self._reader.speaking_timer.get_speaking(ssrc)
