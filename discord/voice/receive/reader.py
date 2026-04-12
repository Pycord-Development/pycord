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

from ..packets.core import OPUS_SILENCE
from ..packets.rtp import ReceiverReportPacket, RTCPPacket, decode
from ..utils.dependencies import HAS_DAVEY, HAS_NACL
from .router import PacketRouter, SinkEventRouter

if HAS_DAVEY:
    import davey

if HAS_NACL:
    import nacl.secret
    from nacl.exceptions import CryptoError


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
        self,
        sink: Sink,
        client: VoiceClient,
        *,
        after: AfterCallback | None = None,
        start: bool = False,
    ) -> None:
        if after is not None and not callable(after):
            raise TypeError(
                f"expected a callable for the 'after' parameter, got {after.__class__.__name__!r} instead"
            )

        self.sink: Sink = sink
        self.client: VoiceClient = client
        self.after: AfterCallback | None = after

        self.sink.init(client)

        self.active: bool = False
        self.error: Exception | None = None
        self.packet_router: PacketRouter = PacketRouter(self.sink, self)
        self.event_router: SinkEventRouter = SinkEventRouter(self.sink, self)
        self.decryptor: PacketDecryptor = PacketDecryptor(
            client.mode, bytes(client.secret_key), client
        )
        self.speaking_timer: SpeakingTimer = SpeakingTimer(self)
        self.keep_alive: UDPKeepAlive = UDPKeepAlive(client)

        if start:
            self.start()

    def is_listening(self) -> bool:
        return self.active

    def update_secret_key(self, secret_key: bytes) -> None:
        self.decryptor.update_secret_key(secret_key)

    def start(self) -> None:
        if self.active:
            _log.debug("Reader is already running", exc_info=True)
            return

        self.client._connection.add_socket_listener(self.callback)
        self.speaking_timer.start()
        self.event_router.start()
        self.packet_router.start()
        self.keep_alive.start()
        self.active = True

    def stop(self) -> None:
        if not self.active:
            _log.debug("Reader is not active")
            return

        self.client._connection.remove_socket_listener(self.callback)
        self.speaking_timer.notify()
        self._stop()
        self.active = False

    def _stop(self) -> None:
        try:
            if self.packet_router.is_alive():
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

        """for sink in self.sink.root.walk_children(with_self=True):
            try:
                sink.cleanup()
            except Exception as exc:
                _log.exception("Error calling cleanup() for %s", sink, exc_info=exc)"""

    def set_sink(self, sink: Sink) -> Sink:
        old_sink = self.sink
        # old_sink._client = None
        # sink._client = self.client
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
                _log.debug("Callback errored out, stopping: %s", self.error)
                self.stop()
                return
            if not packet:
                _log.debug("No packet found after callback")
                return

        if rtcp_packet:
            self.packet_router.feed_rtcp(rtcp_packet)  # type: ignore
        elif rtp_packet:

            if not rtp_packet.decrypted_data:
                _log.debug(
                    "No decrypted data for RTP packet, this should be safe to ignore."
                )
                return

            ssrc = rtp_packet.ssrc

            if ssrc not in self.client._connection.ssrc_user_map:
                if rtp_packet.is_silence():
                    return
                else:
                    _log.info(
                        "Received a packet for unknown SSRC %s: %s", ssrc, rtp_packet
                    )
                    _log.debug(
                        "Current SSRCs: %s", self.client._connection.ssrc_user_map
                    )

            self.speaking_timer.notify(ssrc)

            try:
                _log.debug("Feeding packet to packet router")
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

    """def decrypt_rtp(self, packet: RTPPacket) -> bytes:
        state = self.client._connection
        dave = state.dave_session
        data = self._decryptor_rtp(packet)

        if dave is not None and dave.ready and packet.ssrc in state.ssrc_user_map:
            data = dave.decrypt(
                state.ssrc_user_map[packet.ssrc], davey.MediaType.audio, data
            )

        if packet.extended:
            offset = packet.update_extended_header(data)
            data = data[offset:]

        return data"""

    # Per-SSRC counters used to suppress repetitive log lines.
    _dave_success: dict[int, int] = {}
    _dave_consecutive_failures: dict[int, int] = {}
    _dave_seen_generations: dict[int, set] = {}

    @staticmethod
    def _parse_dave_generation(data: bytes) -> int:
        """Return the key generation encoded in a DAVE supplemental block, or -1.

        DAVE frame layout (from end of payload):
          [...ciphertext][auth_tag(8B)][nonce(LEB128)][supp_size(1B)][0xFAFA(2B)]
        supp_size counts the entire trailing block including itself and the magic.
        """
        if len(data) < 12:
            return -1
        if data[-2:] != b'\xfa\xfa':
            return -1
        supp_size = data[-3]
        if supp_size < 11 or supp_size > len(data):
            return -1
        block_start = len(data) - supp_size
        nonce_pos = block_start + 8  # skip auth_tag (8B)
        nonce_end = len(data) - 3   # position of supp_size byte
        nonce = 0
        shift = 0
        for i in range(nonce_pos, nonce_end):
            b = data[i]
            nonce |= (b & 0x7F) << shift
            shift += 7
            if not (b & 0x80):
                break
        return (nonce >> 24) & 0xFF

    def decrypt_rtp(self, packet: RTPPacket) -> bytes:
        state = self.client._connection
        dave = state.dave_session

        raw_payload = self._decryptor_rtp(packet)

        # For extended RTP packets (which Discord always sends for audio),
        # _decryptor_rtp already strips the RTP extension values so that
        # davey.decrypt() receives only the DAVE frame.  For non-extended
        # packets fall back to the full outer-decrypted buffer.
        if packet.extended:
            dave_input = raw_payload
        else:
            dave_input = getattr(packet, '_outer_decrypted', raw_payload)

        if dave is not None and dave.ready:
            uid = state.ssrc_user_map.get(packet.ssrc)
            if uid:
                try:
                    decrypted_audio = dave.decrypt(
                        uid,
                        davey.MediaType.audio,
                        dave_input,
                    )

                    success_count = self._dave_success.get(packet.ssrc, 0) + 1
                    self._dave_success[packet.ssrc] = success_count
                    prev_fails = self._dave_consecutive_failures.get(packet.ssrc, 0)
                    self._dave_consecutive_failures[packet.ssrc] = 0

                    if success_count == 1:
                        _log.debug("DAVE decrypt active ssrc=%s uid=%s", packet.ssrc, uid)
                    elif prev_fails > 0:
                        _log.info(
                            "DAVE decrypt recovered ssrc=%s uid=%s after %d frame(s)",
                            packet.ssrc, uid, prev_fails,
                        )

                    # DAVE output is pure Opus — do NOT call update_extended_header;
                    # it would misinterpret Opus bytes as RTP extension values.
                    packet.decrypted_data = decrypted_audio

                except Exception as exc:
                    consec = self._dave_consecutive_failures.get(packet.ssrc, 0) + 1
                    self._dave_consecutive_failures[packet.ssrc] = consec
                    gen = self._parse_dave_generation(dave_input)
                    seen = self._dave_seen_generations.setdefault(packet.ssrc, set())

                    # Log on the first failure in a burst or when a new generation appears.
                    if consec == 1 or gen not in seen:
                        _log.warning(
                            "DAVE decrypt failed ssrc=%s uid=%s frame_gen=%s epoch=%s err=%s",
                            packet.ssrc, uid, gen, dave.epoch, type(exc).__name__,
                        )
                        seen.add(gen)

                    if "UnencryptedWhenPassthroughDisabled" in str(exc):
                        # Discord sends passthrough (unencrypted) frames even while DAVE
                        # is active.  These carry raw Opus wrapped in a small DAVE
                        # supplemental block with optional RTP padding appended:
                        #
                        #   [raw_opus][supp_block(supp_size B)][rtp_padding]
                        #
                        # supp_block ends with supp_size(1B) + 0xFAFA(2B); supp_size
                        # counts the whole block including itself and the magic bytes.
                        # RTP padding (RFC 3550): last byte = N, strip N bytes from end.
                        opus_data = raw_payload
                        if packet.padding and opus_data:
                            pad_n = opus_data[-1]
                            if 0 < pad_n < len(opus_data):
                                opus_data = opus_data[:-pad_n]
                        if len(opus_data) >= 3 and opus_data[-2:] == b'\xfa\xfa':
                            supp_size = opus_data[-3]
                            if 3 <= supp_size < len(opus_data):
                                opus_data = opus_data[:-supp_size]
                                packet.decrypted_data = opus_data if len(opus_data) >= 3 else OPUS_SILENCE
                            else:
                                packet.decrypted_data = OPUS_SILENCE
                        else:
                            packet.decrypted_data = OPUS_SILENCE
                    else:
                        packet.decrypted_data = OPUS_SILENCE

        if packet.decrypted_data is None:
            if dave is None:
                # Non-DAVE mode: outer-decrypted bytes ARE the Opus payload.
                if packet.extended:
                    offset = packet.update_extended_header(raw_payload)
                    packet.decrypted_data = raw_payload[offset:]
                else:
                    packet.decrypted_data = raw_payload
            else:
                # DAVE session not ready yet or SSRC not yet mapped — use Opus
                # silence to avoid feeding ciphertext to the Opus decoder.
                packet.decrypted_data = OPUS_SILENCE

        return packet.decrypted_data

    def decrypt_rtcp(self, packet: bytes) -> bytes:
        data = self._decryptor_rtcp(packet)

        # parse the rtcp packet to its respective report type
        offset = 0

        while offset < len(data):
            # offset will allow us to read the compund packets
            current_data = data[offset:]
            if len(current_data) < 8:
                break

            p_header = RTCPPacket.from_data(current_data)

            # the sender ssrc will always be at offset 4 of the current packet
            # doesn't matter if it is a sr or a rr
            ssrc = p_header.ssrc

            state = self.client._connection
            dave = state.dave_session

            if dave is not None and dave.ready and ssrc in state.ssrc_user_map:
                return dave.decrypt(
                    state.ssrc_user_map[ssrc],
                    davey.MediaType.audio,
                    current_data,
                )
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
        nonce = packet.nonce + b"\x00" * 20

        assert isinstance(self.box, nacl.secret.Aead)

        try:
            result = self.box.decrypt(
                packet.decrypted_data or packet.data,
                bytes(packet.header),
                nonce,
            )
        except Exception as exc:
            _log.error("Critical error at AEAD: %s", exc)
            raise CryptoError(exc)

        # update_extended_header returns the actual payload offset into result.
        # For Discord DAVE frames the extension has length=2 (8 bytes) → offset=8.
        # For passthrough/unencrypted frames the extension has length=1 (4 bytes)
        # → offset=4.  Hardcoding result[8:] would strip 4 bytes too many for
        # passthrough frames and hand invalid bytes to davey / the Opus decoder.
        if packet.extended:
            offset = packet.update_extended_header(result)
        else:
            offset = 0

        packet._outer_decrypted = result
        return result[offset:]

    def _decrypt_rtcp_aead_xchacha20_poly1305_rtpsize(self, data: bytes) -> bytes:
        _log.debug("Decrypting RTCP AEAD XChaCha20 Poly1305 RTPSize")
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
        id = self.client._connection.ssrc_user_map.get(ssrc)
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
