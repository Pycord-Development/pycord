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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Final

OPUS_SILENCE: Final = b"\xf8\xff\xfe"


class Packet:
    """Represents an audio stream bytes packet.

    Attributes
    ----------
    data: :class:`bytes`
        The bytes data of this packet. This has not been decoded.
    """

    if TYPE_CHECKING:
        ssrc: int
        sequence: int
        timestamp: int
        type: int
        decrypted_data: bytes

    def __init__(self, data: bytes) -> None:
        self.data: bytes = data

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}> data={len(self.data)} bytes>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        if self.ssrc != other.ssrc:
            raise TypeError(
                f"cannot compare two packets from different ssrc ({self.ssrc=}, {other.ssrc=})"
            )
        return self.sequence == other.sequence and self.timestamp == other.timestamp

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        if self.ssrc != other.ssrc:
            raise TypeError(
                f"cannot compare two packets from different ssrc ({self.ssrc=}, {other.ssrc=})"
            )
        return self.sequence > other.sequence and self.timestamp > other.timestamp

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        if self.ssrc != other.ssrc:
            raise TypeError(
                f"cannot compare two packets from different ssrc ({self.ssrc=}, {other.ssrc=})"
            )
        return self.sequence < other.sequence and self.timestamp < other.timestamp

    def is_silence(self) -> bool:
        data = getattr(self, "decrypted_data", None)
        return data == OPUS_SILENCE

    def __hash__(self) -> int:
        return hash(self.data)
