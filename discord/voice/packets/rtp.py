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

import struct
from collections import namedtuple
from typing import TYPE_CHECKING, Any, Literal

from .core import OPUS_SILENCE, Packet

if TYPE_CHECKING:
    from typing_extensions import Final

MAX_UINT_32 = 0xFFFFFFFF
MAX_UINT_16 = 0xFFFF

RTP_PACKET_TYPE_VOICE = 120


def decode(data: bytes) -> Packet:
    if not data[0] >> 6 == 2:
        raise ValueError(f"Invalid packet header 0b{data[0]:0>8b}")
    return _rtcp_map.get(data[1], RTPPacket)(data)


class FakePacket(Packet):
    data = b""
    decrypted_data: bytes = b""
    extension_data: dict = {}

    def __init__(
        self,
        ssrc: int,
        sequence: int,
        timestamp: int,
    ) -> None:
        self.ssrc = ssrc
        self.sequence = sequence
        self.timestamp = timestamp

    def __bool__(self) -> Literal[False]:
        return False


class SilencePacket(Packet):
    decrypted_data: Final = OPUS_SILENCE
    extension_data: Final[dict[int, Any]] = {}
    sequence: int = -1

    def __init__(self, ssrc: int, timestamp: int) -> None:
        self.ssrc = ssrc
        self.timestamp = timestamp

    def is_silence(self) -> bool:
        return True


class RTPPacket(Packet):
    """Represents an RTP packet.

    .. versionadded:: 2.7

    Attributes
    ----------
    data: :class:`bytes`
        The raw data of the packet.
    """

    _hstruct = struct.Struct(">xxHII")
    _ext_header = namedtuple("Extension", "profile length values")
    _ext_magic = b"\xbe\xde"

    def __init__(self, data: bytes) -> None:
        super().__init__(data)

        self.version: int = data[0] >> 6
        self.padding: bool = bool(data[0] & 0b00100000)
        self.extended: bool = bool(data[0] & 0b00010000)
        self.cc: int = data[0] & 0b00001111

        self.marker: bool = bool(data[1] & 0b10000000)
        self.payload: int = data[1] & 0b01111111

        sequence, timestamp, ssrc = self._hstruct.unpack_from(data)
        self.sequence = sequence
        self.timestamp = timestamp
        self.ssrc = ssrc

        self.csrcs: tuple[int, ...] = ()
        self.extension = None
        self.extension_data: dict[int, bytes] = {}

        self.header = data[:12]
        self.data = data[12:]
        self.decrypted_data: bytes | None = None

        self.nonce: bytes = b""
        self._rtpsize: bool = False

        if self.cc:
            fmt = ">%sI" % self.cc
            offset = struct.calcsize(fmt) + 12
            self.csrcs = struct.unpack(fmt, data[12:offset])
            self.data = data[offset:]

    def adjust_rtpsize(self) -> None:
        """Automatically adjusts this packet header and data based on the rtpsize format."""

        self._rtpsize = True
        self.nonce = self.data[-4:]

        if not self.extended:
            self.data = self.data[:-4]
            return

        self.header += self.data[:4]
        self.data = self.data[4:-4]

    def update_extended_header(self, data: bytes) -> int:
        """Updates the extended header using ``data`` and returns the pd offset."""

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
            el_id = header >> 4
            el_len = 1 + (header & 0b0000_1111)

            self.extension_data[el_id] = data[offset + 1 : offset + 1 + el_len]
            offset += 1 + el_len
            n += 1

    def __repr__(self) -> str:
        return (
            "<RTPPacket "
            f"ssrc={self.ssrc} "
            f"sequence={self.sequence} "
            f"timestamp={self.timestamp} "
            f"size={len(self.data)} "
            f"ext={set(self.extension_data)}"
            ">"
        )


class RTCPPacket(Packet):
    _header = struct.Struct(">BBH")
    _ssrc_fmt = struct.Struct(">I")
    type = None

    def __init__(self, data: bytes) -> None:
        super().__init__(data)
        self.length: int
        head, _, self.length = self._header.unpack_from(data)

        self.version: int = head >> 6
        self.padding: bool = bool(head & 0b00100000)
        setattr(self, "report_count", head & 0b00011111)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} version={self.version} padding={self.padding} length={self.length}>"

    @classmethod
    def from_data(cls, data: bytes) -> Packet:
        _, ptype, _ = cls._header.unpack_from(data)
        return _rtcp_map[ptype](data)


def _parse_low(x: int, bitlen: int = 32) -> float:
    return x / 2.0**bitlen


def _to_low(x: float, bitlen: int = 32) -> int:
    return int(x * 2.0**bitlen)


class SenderReportPacket(RTCPPacket):
    _info_fmt = struct.Struct(">5I")
    _report_fmt = struct.Struct(">IB3x4I")
    _24bit_int_fmt = struct.Struct(">4xI")
    _info = namedtuple("RRSenderInfo", "ntp_ts rtp_ts packet_count octet_count")
    _report = namedtuple(
        "RReport", "ssrc perc_loss total_lost last_seq jitter lsr dlsr"
    )
    type = 200

    if TYPE_CHECKING:
        report_count: int

    def __init__(self, data: bytes) -> None:
        super().__init__(data)

        self.ssrc = self._ssrc_fmt.unpack_from(data, 4)[0]
        self.info = self._read_sender_info(data, 8)

        _report = self._report
        reports: list[_report] = []
        for x in range(self.report_count):
            offset = 28 + 24 * x
            reports.append(self._read_report(data, offset))

        self.reports: tuple[_report, ...] = tuple(reports)
        self.extension = None
        if len(data) > 28 + 24 * self.report_count:
            self.extension = data[28 + 24 * self.report_count :]

    def _read_sender_info(self, data: bytes, offset: int) -> _info:
        nhigh, nlow, rtp_ts, pcount, ocount = self._info_fmt.unpack_from(data, offset)
        ntotal = nhigh + _parse_low(nlow)
        return self._info(ntotal, rtp_ts, pcount, ocount)

    def _read_report(self, data: bytes, offset: int) -> _report:
        ssrc, flost, seq, jit, lsr, dlsr = self._report_fmt.unpack_from(data, offset)
        clost = self._24bit_int_fmt.unpack_from(data, offset)[0] & 0xFFFFFF
        return self._report(ssrc, flost, clost, seq, jit, lsr, dlsr)


class ReceiverReportPacket(RTCPPacket):
    _report_fmt = struct.Struct(">IB3x4I")
    _24bit_int_fmt = struct.Struct(">4xI")
    _report = namedtuple(
        "RReport", "ssrc perc_loss total_loss last_seq jitter lsr dlsr"
    )
    type = 201

    reports: tuple[_report, ...]

    if TYPE_CHECKING:
        report_count: int

    def __init__(self, data: bytes) -> None:
        super().__init__(data)
        self.ssrc: int = self._ssrc_fmt.unpack_from(data, 4)[0]

        _report = self._report
        reports: list[_report] = []
        for x in range(self.report_count):
            offset = 8 + 24 * x
            reports.append(self._read_report(data, offset))

        self.reports = tuple(reports)

        self.extension: bytes | None = None
        if len(data) > 8 + 24 * self.report_count:
            self.extension = data[8 + 24 * self.report_count :]

    def _read_report(self, data: bytes, offset: int) -> _report:
        ssrc, flost, seq, jit, lsr, dlsr = self._report_fmt.unpack_from(data, offset)
        clost = self._24bit_int_fmt.unpack_from(data, offset)[0] & 0xFFFFFF
        return self._report(ssrc, flost, clost, seq, jit, lsr, dlsr)


_rtcp_map = {
    200: SenderReportPacket,
    201: ReceiverReportPacket,
}
