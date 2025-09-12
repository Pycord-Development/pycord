"""
The MIT License (MIT)

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

from collections.abc import Callable
from typing import IO, TYPE_CHECKING, Any, overload

from discord.utils import MISSING

from .core import FFmpegSink

if TYPE_CHECKING:
    from typing_extensions import Self

    from discord.voice import VoiceData

__all__ = ("MKVSink",)


class MKVSink(FFmpegSink):
    """A special sink for .mkv files.

    .. versionadded:: 2.0

    Parameters
    ----------
    filename: :class:`str`
        The file in which the recording will be saved into.
        This can't be mixed with ``buffer``.

        .. versionadded:: 2.7
    buffer: IO[:class:`bytes`]
        The buffer in which the recording will be saved into.
        This can't be mixed with ``filename``.

        .. verionadded:: 2.7
    executable: :class:`str`
        The executable in which ``ffmpeg`` is in.

        .. versionadded:: 2.7
    stderr: IO[:class:`bytes`] | :data:`None`
        The stderr buffer in which will be written. Defaults to ``None``.
    
        .. versionadded:: 2.7
    options: :class:`str` | :data:`None`
        The options to append to the ffmpeg executable flags. You should not
        use this because you may override any already-provided flag.

        .. versionadded:: 2.7
    error_hook: Callable[[:class:`FFmpegSink`, :class:`Exception`, :class:`discord.voice.VoiceData` | :data:`None`], Any] | :data:`None`
        The callback to call when an error ocurrs with this sink.

        .. versionadded:: 2.7
    """

    @overload
    def __init__(
        self,
        *,
        filename: str,
        executable: str = ...,
        stderr: IO[bytes] | None = ...,
        options: str | None = ...,
        error_hook: Callable[[Self, Exception, VoiceData | None], Any] | None = ...,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        buffer: IO[bytes],
        executable: str = ...,
        stderr: IO[bytes] | None = ...,
        options: str | None = ...,
        error_hook: Callable[[Self, Exception, VoiceData | None], Any] | None = ...,
    ) -> None: ...

    def __init__(
        self,
        *,
        filename: str = MISSING,
        buffer: IO[bytes] = MISSING,
        executable: str = "ffmpeg",
        stderr: IO[bytes] | None = None,
        options: str | None = None,
        error_hook: Callable[[Self, Exception, VoiceData | None], Any] | None = None,
    ) -> None:
        super().__init__(
            executable=executable,
            before_options="-f matroska -loglevel error",
            filename=filename,
            buffer=buffer,
            stderr=stderr,
            options=options,
            error_hook=error_hook,
        )  # type: ignore
