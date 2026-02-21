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
import threading
import time
from collections.abc import Callable
from operator import itemgetter
from typing import TYPE_CHECKING, Any, Literal

import davey

from discord.opus import PacketDecoder

from ..packets.rtp import ReceiverReportPacket, decode
from .router import PacketRouter, SinkEventRouter

try:
    import nacl.secret
    from nacl.exceptions import CryptoError
except ImportError as exc:
    raise RuntimeError(
        "can't use voice receiver without PyNaCl installed, please install it with the 'py-cord[voice]' extra."
    ) from exc


if TYPE_CHECKING:
    from discord.member import Member
    from discord.sinks import Sink
    from discord.types.voice import SupportedModes

    from ..client import VoiceClient
    from ..packets import RTPPacket

    AfterCallback = Callable[[Exception | None], Any]
    DecryptRTP = Callable[[RTPPacket], bytes]
    DecryptRTCP = Callable[[bytes], bytes]
    SpeakingEvent = Literal["member_speaking_start", "member_speaking_stop"]
    EncryptionBox = nacl.secret.SecretBox | nacl.secret.Aead

_log = logging.getLogger(__name__)

__all__ = ("AudioReader",)


def is_rtcp(data: bytes) -> bool:
    return 200 <= data[1] <= 204


class AudioReader:
    def __init__(
        self, sink: Sink, client: VoiceClient, *, after: AfterCallback | None = None
    ) -> None:
        if after is not None and not callable(after):
            raise TypeError(
                f"expected a callable for the 'after' parameter, got {after.__class__.__name__!r} instead"
            )

        self.sink: Sink = sink
        self.client: VoiceClient = client
        self.after: AfterCallback | None = after

        self.sink._client = client

        self.active: bool = False
        self.error: Exception | None = None
        self.packet_router: PacketRouter = PacketRouter(self.sink, self)
        self.event_router: SinkEventRouter = SinkEventRouter(self.sink, self)
        self.decryptor: PacketDecryptor = PacketDecryptor(
            client.mode, bytes(client.secret_key), client
        )
        self.speaking_timer: SpeakingTimer = SpeakingTimer(self)
        self.keep_alive: UDPKeepAlive = UDPKeepAlive(client)

    def is_listening(self) -> bool:
        return self.active

    def update_secret_key(self, secret_key: bytes) -> None:
        self.decryptor.update_secret_key(secret_key)

    def start(self) -> None:
        if self.active:
            _log.debug("Reader is already running", exc_info=True)
            return

        self.speaking_timer.start()
        self.event_router.start()
        self.packet_router.start()
        self.client._connection.add_socket_listener(self.callback)
        self.keep_alive.start()
        self.active = True

    def stop(self) -> None:
        if not self.active:
            _log.debug("Reader is not active", exc_info=True)
            return

        self.client._connection.remove_socket_listener(self.callback)
        self.active = False
        self.speaking_timer.notify()

        threading.Thread(
            target=self._stop, name=f"voice-receiver-audio-reader-stop:{id(self):#x}"
        ).start()

    def _stop(self) -> None:
        try:
            self.packet_router.stop()
        except Exception as exc:
            self.error = exc
            _log.exception("An error ocurred while stopping packet router.")

        try:
            self.event_router.stop()
        except Exception as exc:
            self.error = exc
            _log.exception("An error ocurred while stopping event router.")

        self.speaking_timer.stop()
        self.keep_alive.stop()

        if self.after:
            try:
                self.after(self.error)
            except Exception:
                _log.exception(
                    "An error ocurred while calling the after callback on audio reader"
                )

        for sink in self.sink.root.walk_children(with_self=True):
            try:
                sink.cleanup()
            except Exception as exc:
                _log.exception("Error calling cleanup() for %s", sink, exc_info=exc)

    def set_sink(self, sink: Sink) -> Sink:
        old_sink = self.sink
        old_sink._client = None
        sink._client = self.client
        self.packet_router.set_sink(sink)
        self.sink = sink
        return old_sink

    def _is_ip_discovery_packet(self, data: bytes) -> bool:
        return len(data) == 74 and data[1] == 0x02

    def callback(self, packet_data: bytes) -> None:

        packet = rtp_packet = rtcp_packet = None

        try:
            if not is_rtcp(packet_data):
                packet = rtp_packet = decode(packet_data)
                packet.decrypted_data = self.decryptor.decrypt_rtp(packet)  # type: ignore
            else:
                packet = rtcp_packet = decode(packet_data)

                if not isinstance(packet, ReceiverReportPacket):
                    _log.info(
                        "Received unexpected rtcp packet type=%s, %s",
                        packet.type,
                        type(packet),
                    )
        except CryptoError as exc:
            _log.error("CryptoError while decoding a voice packet", exc_info=exc)
            return
        except Exception as exc:
            if self._is_ip_discovery_packet(packet_data):
                _log.debug("Received an IP Discovery Packet, ignoring...")
                return
            _log.exception(
                "An exception ocurred while decoding voice packets", exc_info=exc
            )
        finally:
            if self.error:
                self.stop()
                return
            if not packet:
                return

        if rtcp_packet:
            self.packet_router.feed_rtcp(rtcp_packet)  # type: ignore
        elif rtp_packet:
            ssrc = rtp_packet.ssrc

            if ssrc not in self.client._connection.user_ssrc_map:
                if rtp_packet.is_silence():
                    return
                else:
                    _log.info(
                        "Received a packet for unknown SSRC %s: %s", ssrc, rtp_packet
                    )

            self.speaking_timer.notify(ssrc)

            try:
                self.packet_router.feed_rtp(rtp_packet)  # type: ignore
            except Exception as exc:
                _log.exception(
                    "An error ocurred while processing RTP packet %s", rtp_packet
                )
                self.error = exc
                self.stop()


class PacketDecryptor:
    supported_modes: list[SupportedModes] = [
        "aead_xchacha20_poly1305_rtpsize",
        "xsalsa20_poly1305",
        "xsalsa20_poly1305_lite",
        "xsalsa20_poly1305_suffix",
    ]

    def __init__(
        self, mode: SupportedModes, secret_key: bytes, client: VoiceClient
    ) -> None:
        self.mode: SupportedModes = mode
        self.client: VoiceClient = client

        try:
            self._decryptor_rtp: DecryptRTP = getattr(self, "_decrypt_rtp_" + mode)
            self._decryptor_rtcp: DecryptRTCP = getattr(self, "_decrypt_rtcp_" + mode)
        except AttributeError as exc:
            raise NotImplementedError(mode) from exc

        self.box: EncryptionBox = self._make_box(secret_key)

    def _make_box(self, secret_key: bytes) -> EncryptionBox:
        if self.mode.startswith("aead"):
            return nacl.secret.Aead(secret_key)
        else:
            return nacl.secret.SecretBox(secret_key)

    def decrypt_rtp(self, packet: RTPPacket) -> bytes:
        state = self.client._connection
        dave = state.dave_session
        data = self._decryptor_rtp(packet)

        if dave is not None and dave.ready and packet.ssrc in state.user_ssrc_map:
            return dave.decrypt(
                state.user_ssrc_map[packet.ssrc], davey.MediaType.audio, data
            )
        return data

    def decrypt_rtcp(self, packet: bytes) -> bytes:
        data = self._decryptor_rtcp(packet)
        # TODO: guess how to get the SSRC so we can use dave
        return data

    def update_secret_key(self, secret_key: bytes) -> None:
        self.box = self._make_box(secret_key)

    def _decrypt_rtp_xsalsa20_poly1305(self, packet: RTPPacket) -> bytes:
        nonce = bytearray(24)
        nonce[:12] = packet.header
        result = self.box.decrypt(bytes(packet.data), bytes(nonce))

        if packet.extended:
            offset = packet.update_extended_header(result)
            result = result[offset:]

        return result

    def _decrypt_rtcp_xsalsa20_poly1305(self, data: bytes) -> bytes:
        nonce = bytearray(24)
        nonce[:8] = data[:8]
        result = self.box.decrypt(data[8:], bytes(nonce))

        return data[:8] + result

    def _decrypt_rtp_xsalsa20_poly1305_suffix(self, packet: RTPPacket) -> bytes:
        nonce = packet.data[-24:]
        voice_data = packet.data[:-24]
        result = self.box.decrypt(bytes(voice_data), bytes(nonce))

        if packet.extended:
            offset = packet.update_extended_header(result)
            result = result[offset:]

        return result

    def _decrypt_rtcp_xsalsa20_poly1305_suffix(self, data: bytes) -> bytes:
        nonce = data[-24:]
        header = data[:8]
        result = self.box.decrypt(data[8:-24], nonce)

        return header + result

    def _decrypt_rtp_xsalsa20_poly1305_lite(self, packet: RTPPacket) -> bytes:
        nonce = bytearray(24)
        nonce[:4] = packet.data[-4:]
        voice_data = packet.data[:-4]
        result = self.box.decrypt(bytes(voice_data), bytes(nonce))

        if packet.extended:
            offset = packet.update_extended_header(result)
            result = result[offset:]

        return result

    def _decrypt_rtcp_xsalsa20_poly1305_lite(self, data: bytes) -> bytes:
        nonce = bytearray(24)
        nonce[:4] = data[-4:]
        header = data[:8]
        result = self.box.decrypt(data[8:-4], bytes(nonce))

        return header + result

    def _decrypt_rtp_aead_xchacha20_poly1305_rtpsize(self, packet: RTPPacket) -> bytes:
        packet.adjust_rtpsize()

        nonce = bytearray(24)
        nonce[:4] = packet.nonce
        voice_data = packet.data

        # Blob vomit
        assert isinstance(self.box, nacl.secret.Aead)
        result = self.box.decrypt(bytes(voice_data), bytes(packet.header), bytes(nonce))

        if packet.extended:
            offset = packet.update_extended_header(result)
            result = result[offset:]

        return result

    def _decrypt_rtcp_aead_xchacha20_poly1305_rtpsize(self, data: bytes) -> bytes:
        nonce = bytearray(24)
        nonce[:4] = data[-4:]
        header = data[:8]

        assert isinstance(self.box, nacl.secret.Aead)
        result = self.box.decrypt(data[8:-4], bytes(header), bytes(nonce))

        return header + result


class SpeakingTimer(threading.Thread):
    def __init__(self, reader: AudioReader) -> None:
        super().__init__(
            daemon=True,
            name=f"voice-receiver-speaking-timer:{id(self):#x}",
        )

        self.reader: AudioReader = reader
        self.client: VoiceClient = reader.client
        self.speaking_timeout_delay: float = 0.2
        self.last_speaking_state: dict[int, bool] = {}
        self.speaking_cache: dict[int, float] = {}
        self.speaking_timer_event: threading.Event = threading.Event()
        self._end_thread: threading.Event = threading.Event()

    def _lookup_member(self, ssrc: int) -> Member | None:
        id = self.client._connection.user_ssrc_map.get(ssrc)
        if not self.client.guild:
            return None
        return self.client.guild.get_member(id) if id else None

    def maybe_dispatch_speaking_start(self, ssrc: int) -> None:
        tlast = self.speaking_cache.get(ssrc)
        if tlast is None or tlast + self.speaking_timeout_delay < time.perf_counter():
            self.dispatch("member_speaking_start", ssrc)

    def dispatch(self, event: SpeakingEvent, ssrc: int) -> None:
        member = self._lookup_member(ssrc)
        if not member:
            return None
        self.client._dispatch_sink(event, member)

    def notify(self, ssrc: int | None = None) -> None:
        if ssrc is not None:
            self.last_speaking_state[ssrc] = True
            self.maybe_dispatch_speaking_start(ssrc)
            self.speaking_cache[ssrc] = time.perf_counter()

        self.speaking_timer_event.set()
        self.speaking_timer_event.clear()

    def drop_ssrc(self, ssrc: int) -> None:
        self.speaking_cache.pop(ssrc, None)
        state = self.last_speaking_state.pop(ssrc, None)
        if state:
            self.dispatch("member_speaking_stop", ssrc)
        self.notify()

    def get_speaking(self, ssrc: int) -> bool | None:
        return self.last_speaking_state.get(ssrc)

    def stop(self) -> None:
        self._end_thread.set()
        self.notify()

    def run(self) -> None:
        _i1 = itemgetter(1)

        def get_next_entry():
            cache = sorted(self.speaking_cache.items(), key=_i1)
            for ssrc, tlast in cache:
                if self.last_speaking_state.get(ssrc):
                    return ssrc, tlast
            return None, None

        self.speaking_timer_event.wait()
        while not self._end_thread.is_set():
            if not self.speaking_cache:
                self.speaking_timer_event.wait()

            tnow = time.perf_counter()
            ssrc, tlast = get_next_entry()

            if ssrc is None or tlast is None:
                self.speaking_timer_event.wait()
                continue

            self.speaking_timer_event.wait(tlast + self.speaking_timeout_delay - tnow)

            if time.perf_counter() < tlast + self.speaking_timeout_delay:
                continue

            self.dispatch("member_speaking_stop", ssrc)
            self.last_speaking_state[ssrc] = False


class UDPKeepAlive(threading.Thread):
    delay: int = 5000

    def __init__(self, client: VoiceClient) -> None:
        super().__init__(
            daemon=True,
            name=f"voice-receiver-udp-keep-alive:{id(self):#x}",
        )

        self.client: VoiceClient = client
        self.last_time: float = 0
        self.counter: int = 0
        self._end_thread: threading.Event = threading.Event()

    def run(self) -> None:
        self.client.wait_until_connected()

        while not self._end_thread.is_set():
            vc = self.client

            try:
                packet = self.counter.to_bytes(8, "big")
            except OverflowError:
                self.counter = 0
                continue

            try:
                vc._connection.socket.sendto(
                    packet, (vc._connection.endpoint_ip, vc._connection.voice_port)
                )
            except Exception as exc:
                _log.debug(
                    "Error while sending udp keep alive to socket %s at %s:%s",
                    vc._connection.socket,
                    vc._connection.endpoint_ip,
                    vc._connection.voice_port,
                    exc_info=exc,
                )
                vc.wait_until_connected()
                if vc.is_connected():
                    continue
                break
            else:
                self.counter += 1
                time.sleep(self.delay)

    def stop(self) -> None:
        self._end_thread.set()
