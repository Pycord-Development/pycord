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
import struct
from typing import TYPE_CHECKING, Any, Literal, overload

from discord import opus
from discord.errors import ClientException
from discord.sinks.errors import RecordingException
from discord.utils import MISSING
from discord.sinks import RawData, Sink

from ._types import VoiceProtocol
from .state import VoiceConnectionState
from .recorder import Recorder
from .source import AudioSource
from .player import AudioPlayer

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    from discord import abc
    from discord.client import Client
    from discord.guild import Guild, VocalGuildChannel
    from discord.state import ConnectionState
    from discord.user import ClientUser
    from discord.raw_models import (
        RawVoiceStateUpdateEvent,
        RawVoiceServerUpdateEvent,
    )
    from discord.types.voice import SupportedModes
    from discord.opus import Encoder, APPLICATION_CTL, BAND_CTL, SIGNAL_CTL, Decoder

    from .gateway import VoiceWebSocket

    AfterCallback = Callable[[Exception | None], Any]
    P = ParamSpec('P')

has_nacl: bool

try:
    import nacl.secret
    import nacl.utils
    has_nacl = True
except ImportError:
    has_nacl = False


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

    def __init__(self, client: Client, channel: abc.Connectable) -> None:
        if not has_nacl:
            raise RuntimeError(
                'PyNaCl library is needed in order to use voice related features, '
                'you can run "pip install py-cord[voice]" to install all voice-related '
                'dependencies.'
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
        self.decoder: Decoder = MISSING
        self._incr_nonce: int = 0

        self._connection: VoiceConnectionState = self.create_connection_state()

        # voice recv things
        self._recorder: Recorder | None = None

    warn_nacl: bool = not has_nacl
    supported_modes: tuple[SupportedModes, ...] = (
        'aead_xchacha20_poly1305_rtpsize',
        'xsalsa20_poly1305_lite',
        'xsalsa20_poly1305_suffix',
        'xsalsa20_poly1305',
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
        return VoiceConnectionState(self)

    async def on_voice_state_update(self, data: RawVoiceStateUpdateEvent) -> None:
        await self._connection.voice_state_update(data)

    async def on_voice_server_update(self, data: RawVoiceServerUpdateEvent) -> None:
        await self._connection.voice_server_update(data)

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
        return float('inf') if not ws else ws.latency

    @property
    def average_latency(self) -> float:
        """Average of most recent 20 HEARBEAT latencies in seconds.

        .. versionadded:: 1.4
        """
        ws = self.ws
        return float('inf') if not ws else ws.average_latency

    async def disconnect(self, *, force: bool = False) -> None:
        """|coro|

        Disconnects this voice client from voice.
        """

        self.stop()
        await self._connection.disconnect(force=force, wait=True)
        self.cleanup()

    async def move_to(self, channel: abc.Snowflake | None, *, timeout: float | None = 30.0) -> None:
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
        header = bytearray(12)

        # formulate rtp header
        header[0] = 0x80
        header[1] = 0x78
        struct.pack_into('>H', header, 2, self.sequence)
        struct.pack_into('>I', header, 4, self.timestamp)
        struct.pack_into('>I', header, 8, self.ssrc)

        encrypt_packet = getattr(self, f'_encrypt_{self.mode}')
        return encrypt_packet(header, data)

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
        nonce[:4] = struct.pack('>I', self._incr_nonce)
        self.checked_add('_incr_nonce', 1, 4294967295)

        return header + box.encrypt(bytes(data), bytes(nonce)).ciphertext + nonce[:4]

    def _encrypt_aead_xcacha20_poly1305_rtpsize(self, header: bytes, data: Any) -> bytes:
        box = nacl.secret.Aead(bytes(self.secret_key))
        nonce = bytearray(24)
        nonce[:4] = struct.pack('>I', self._incr_nonce)
        self.checked_add('_incr_nonce', 1, 4294967295)
        return header + box.encrypt(bytes(data), bytes(header), bytes(nonce)).ciphertext + nonce[:4]

    def _decrypt_xsalsa20_poly1305(self, header: bytes, data: Any) -> bytes:
        # deprecated
        box = nacl.secret.SecretBox(bytes(self.secret_key))

        nonce = bytearray(24)
        nonce[:12] = header

        return self.strip_header_ext(box.decrypt(bytes(data), bytes(nonce)))

    def _decrypt_xsalsa20_poly1305_suffix(self, header: bytes, data: Any) -> bytes:
        # deprecated
        box = nacl.secret.SecretBox(bytes(self.secret_key))

        nonce_size = nacl.secret.SecretBox.NONCE_SIZE
        nonce = data[-nonce_size:]

        return self.strip_header_ext(box.decrypt(bytes(data[:-nonce_size]), nonce))

    def _decrypt_xsalsa20_poly1305_lite(self, header: bytes, data: Any) -> bytes:
        # deprecated
        box = nacl.secret.SecretBox(bytes(self.secret_key))

        nonce = bytearray(24)
        nonce[:4] = data[-4:]
        data = data[:-4]

        return self.strip_header_ext(box.decrypt(bytes(data), bytes(nonce)))

    def _decrypt_aead_xchacha20_poly1305_rtpsize(self, header: bytes, data: Any) -> bytes:
        box = nacl.secret.Aead(bytes(self.secret_key))

        nonce = bytearray(24)
        nonce[:4] = data[-4:]
        data = data[:-4]

        return self.strip_header_ext(
            box.decrypt(bytes(data), bytes(header), bytes(nonce))
        )

    @staticmethod
    def strip_header_ext(data: bytes) -> bytes:
        if len(data) > 4 and data[0] == 0xBE and data[1] == 0xDE:
            _, length = struct.unpack_from('>HH', data)
            offset = 4 + length * 4
            data = data[offset:]
        return data

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
        application: APPLICATION_CTL = 'audio',
        bitrate: int = 128,
        fec: bool = True,
        expected_packet_loss: float = 0.15,
        bandwidth: BAND_CTL = 'full',
        signal_type: SIGNAL_CTL = 'auto',
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
            raise ClientException('Not connected to voice')
        if self.is_playing():
            raise ClientException('Already playing audio')
        if not isinstance(source, AudioSource):
            raise TypeError(
                f'Source must be an AudioSource, not {source.__class__.__name__}',
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

        self._player = None
        self._player_future = None

    def unpack_audio(self, data: bytes) -> bytes | None:
        """Takes an audio packet received from Discord and decodes it into PCM Audio data.
        If there are no users talking in the channel, ``None`` will be returned.

        You must be connected to receive audio.

        .. versionadded:: 2.0

        Parameters
        ----------
        data: :class:`bytes`
            Bytes received by Discord via de UDP connection used for sending and receiving voice data.
        """

        if not len(data) > 2:
            return None

        if data[1] != 0x78:
            # We Should Ignore Any Payload Types We Do Not Understand
            # Ref RFC 3550 5.1 payload type
            # At Some Point We Noted That We Should Ignore Only Types 200 - 204 inclusive.
            # They Were Marked As RTCP: Provides Information About The Connection
            # This Was Too Broad Of A Whitelist, It Is Unclear If This Is Too Narrow Of A Whitelist
            return None
        if self.paused:
            return None

        raw = RawData(data, self)

        if raw.decrypted_data == opus.OPUS_SILENCE:  # silenece frame
            return None

        return self.decoder.decode(raw)

    def start_recording(
        self,
        sink: Sink,
        callback: Callable[P, Coroutine[Any, Any, Any]],
        sync_start: bool = False,
        *callback_args: P.args,
        **callback_kwargs: P.kwargs,
    ):
        r"""Start recording audio from the current voice channel. This function uses
        a thread so the current code line will not be stopped. You must be in a voice
        channel to use this, and must not be already recording.

        .. versionadded:: 2.0

        Parameters
        ----------
        sink: :class:`~discord.Sink`
            A Sink which will "store" all the audio data.
        callback: :ref:`coroutine <coroutine>`
            A function which is called after the bot has stopped recording.
        sync_start: :class:`bool`
            If ``True``, the recordings of subsequent users will start with silence. This
            is useful for recording audio just as it was heard.
        \*callback_args
            Arguments that will be passed to the callback function.
        \*\*callback_kwargs
            Keyword arguments that will be passed to the callback function.

        Raises
        ------
        RecordingException
            Not connected to a voice channel, or you are already recording, or you
            did not provide a Sink object.
        """

        if not self.is_connected():
            raise RecordingException('Not connected to a voice channel')
        if self.recording:
            raise RecordingException('You are already recording')
        if not isinstance(sink, Sink):
            raise RecordingException(f'Expected a Sink object, got {sink.__class__.__name__}')

        self._recording_handler.empty()
