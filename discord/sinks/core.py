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

import inspect
import logging
import shlex
import subprocess
import sys
import threading
from collections.abc import Callable, Generator, Sequence
from typing import IO, TYPE_CHECKING, Any, Literal, TypeVar, overload

from typing_extensions import deprecated

from discord.file import File
from discord.player import FFmpegAudio
from discord.utils import MISSING, SequenceProxy

from .errors import FFmpegNotFound

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, Self

    from discord.member import Member
    from discord.user import User
    from discord.voice.packets import VoiceData

    from ..voice.client import VoiceClient

    R = TypeVar("R")
    P = ParamSpec("P")

__all__ = (
    "Sink",
    "RawData",
    "FFmpegSink",
    "FilterSink",
    "MultiSink",
)


if sys.platform != "win32":
    CREATE_NO_WINDOW = 0
else:
    CREATE_NO_WINDOW = 0x08000000


S = TypeVar("S", bound="Sink")
_log = logging.getLogger(__name__)


class SinkMeta(type):
    __sink_listeners__: list[tuple[str, str]]

    def __new__(cls, name, bases, attr, **kwargs):
        listeners = {}

        inst = super().__new__(cls, name, bases, attr, **kwargs)

        for base in reversed(inst.__mro__):
            for elem, value in base.__dict__.items():
                if elem in listeners:
                    del listeners[elem]

                is_static = isinstance(value, staticmethod)
                if is_static:
                    value = value.__func__

                if not hasattr(value, "__sink_listener__"):
                    continue

                listeners[elem] = value

        listeners_list = []
        for listener in listeners.values():
            for listener_name in listener.__sink_listener_names__:
                listeners_list.append((listener_name, listener.__name__))

        inst.__sink_listeners__ = listeners_list
        return inst


class SinkBase(metaclass=SinkMeta):
    """Represents an audio sink in which user's audios are stored."""

    __sink_listeners__: list[tuple[str, str]]
    _client: VoiceClient | None

    @property
    def root(self) -> Sink:
        """Returns the root parent of this sink."""
        return self  # type: ignore

    @property
    def parent(self) -> Sink | None:
        """Returns the parent of this sink."""
        raise NotImplementedError

    @property
    def child(self) -> Sink | None:
        """Returns this sink's child."""
        raise NotImplementedError

    @property
    def children(self) -> Sequence[Sink]:
        """Returns the full list of children of this sink."""
        raise NotImplementedError

    @property
    def client(self) -> VoiceClient | None:
        """Returns the voice client this sink is connected to."""
        return self._client

    def is_opus(self) -> bool:
        """Returns whether this sink is opus."""
        return False

    def write(self, user: User | Member | None, data: VoiceData) -> None:
        """Writes the provided ``data`` into the ``user`` map."""
        raise NotImplementedError

    def cleanup(self) -> None:
        """Cleans this sink."""
        raise NotImplementedError

    def _register_child(self, child: Sink) -> None:
        """Registers a child to this sink."""
        raise NotImplementedError

    def walk_children(self, *, with_self: bool = False) -> Generator[Sink]:
        """Iterates through all the children of this sink, including nested."""
        if with_self:
            yield self  # type: ignore

        for child in self.children:
            yield child
            yield from child.walk_children()

    def __del__(self) -> None:
        self.cleanup()


class Sink(SinkBase):
    """Object that stores the recordings of the audio data.

    Can be subclassed for extra customizability.

    .. versionadded:: 2.0
    """

    _parent: Sink | None = None
    _child: Sink | None = None
    _client = None

    def __init__(self, *, dest: Sink | None = None) -> None:
        if dest is not None:
            self._register_child(dest)
        else:
            self._child = dest

    def _register_child(self, child: Sink) -> None:
        if child in self.root.walk_children():
            raise RuntimeError("Sink is already registered")
        self._child = child
        child._parent = self

    @property
    def root(self) -> Sink:
        if self.parent is None:
            return self
        return self.parent

    @property
    def parent(self) -> Sink | None:
        return self._parent

    @property
    def child(self) -> Sink | None:
        return self._child

    @property
    def children(self) -> Sequence[Sink]:
        return [self._child] if self._child else []

    @property
    def client(self) -> VoiceClient | None:
        if self.parent is not None:
            return self.parent.client
        else:
            return self._client

    @classmethod
    def listener(cls, name: str = MISSING):
        """Registers a sink method as a listener.

        You can stack this decorator and pass the ``name`` parameter to mark the same function
        to listen to various events.

        Parameters
        ----------
        name: :class:`str`
            The name of the event, must not be prefixed with ``on_``. Defaults to the function name.
        """

        if name is not MISSING and not isinstance(name, str):
            raise TypeError(
                f"expected a str for listener name, got {name.__class__.__name__} instead"
            )

        def decorator(func):
            actual = func

            if isinstance(actual, staticmethod):
                actual = actual.__func__

            if inspect.iscoroutinefunction(actual):
                raise TypeError("listener functions must not be coroutines")

            actual.__sink_listener__ = True
            to_assign = name or actual.__name__.removeprefix("on_")

            try:
                actual.__sink_listener_names__.append(to_assign)
            except AttributeError:
                actual.__sink_listener_names__ = [to_assign]

            return func

        return decorator


class MultiSink(Sink):
    """A sink that can handle multiple sinks concurrently.

    .. versionadded:: 2.7
    """

    def __init__(self, *destinations: Sink) -> None:
        for dest in destinations:
            self._register_child(dest)
        self._children: list[Sink] = list(destinations)

    def _register_child(self, child: Sink) -> None:
        if child in self.root.walk_children():
            raise RuntimeError("Sink is already registered")
        child._parent = self

    @property
    def child(self) -> Sink | None:
        return self._children[0] if self._children else None

    @property
    def children(self) -> Sequence[Sink]:
        return SequenceProxy(self._children)

    def add_destination(self, dest: Sink, /) -> None:
        """Adds a sink to be dispatched in this sink.

        Parameters
        ----------
        dest: :class:`Sink`
            The sink to register as this one's child.

        Raises
        ------
        RuntimeError
            The sink is already registered.
        """
        self._register_child(dest)

    def remove_destination(self, dest: Sink, /) -> None:
        """Removes a sink from this sink dispatch.

        Parameters
        ----------
        dest: :class:`Sink`
            The sink to remove.
        """

        try:
            self._children.remove(dest)
        except ValueError:
            pass
        else:
            dest._parent = None


@deprecated(
    "RawData has been deprecated and will be removed in 3.0 in favour of VoiceData",
    category=DeprecationWarning,
)
class RawData:
    def __init__(self, **kwargs: Any) -> None: ...


class FFmpegSink(Sink):
    """A :class:`Sink` built to use ffmpeg executables.

    You can find default implementations of this sink in:

    - :class:`M4ASink`
    - :class:`MKASink`

    .. versionadded:: 2.7

    Parameters
    ----------
    filename: :class:`str`
        The file in which the ffmpeg buffer should be saved to.
        Can not be mixed with ``buffer``.
    buffer: IO[:class:`bytes`]
        The buffer in which the ffmpeg result would be written to.
        Can not be mixed with ``filename``.
    executable: :class:`str`
        The executable in which ``ffmpeg`` is in.
    stderr: IO[:class:`bytes`] | :data:`None`
        The stderr buffer in whcih will be written. Defaults to ``None``.
    before_options: :class:`str` | :data:`None`
        The options to append **before** the default ones.
    options: :class:`str` | :data:`None`
        The options to append **after** the default ones. You can override the
        default ones with this.
    error_hook: Callable[[:class:`FFmpegSink`, :class:`Exception`, :class:`discord.voice.VoiceData` | :data:`None`], Any] | :data:`None`
        The callback to call when an error ocurrs with this sink.
    """

    @overload
    def __init__(
        self,
        *,
        filename: str,
        executable: str = ...,
        stderr: IO[bytes] = ...,
        before_options: str | None = ...,
        options: str | None = ...,
        error_hook: Callable[[Self, Exception, VoiceData | None], Any] | None = ...,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        buffer: IO[bytes],
        executable: str = ...,
        stderr: IO[bytes] = ...,
        before_options: str | None = ...,
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
        before_options: str | None = None,
        options: str | None = None,
        error_hook: Callable[[Self, Exception, VoiceData | None], Any] | None = None,
    ) -> None:
        super().__init__(dest=None)

        if filename is not MISSING and buffer is not MISSING:
            raise TypeError("can't mix filename and buffer parameters")

        self.filename: str = filename or "pipe:1"
        self.buffer: IO[bytes] = buffer

        self.on_error = error_hook or self._on_error

        args = [executable, "-hide_banner"]
        subprocess_kwargs: dict[str, Any] = {"stdin": subprocess.PIPE}
        if self.buffer is not MISSING:
            subprocess_kwargs["stdout"] = subprocess.PIPE

        piping_stderr = False
        if stderr is not None:
            try:
                stderr.fileno()
            except Exception:
                piping_stderr = True
                subprocess_kwargs["stderr"] = subprocess.PIPE

        if isinstance(before_options, str):
            args.extend(shlex.split(before_options))

        args.extend(
            {
                "-f": "s16le",
                "-ar": "48000",
                "-ac": "2",
                "-i": "pipe:0",
                "-loglevel": "warning",
                "-blocksize": str(FFmpegAudio.BLOCKSIZE),
            }
        )

        if isinstance(options, str):
            args.extend(shlex.split(options))

        args.append(self.filename)

        self._process: subprocess.Popen = MISSING
        self._process = self._spawn_process(args, **subprocess_kwargs)

        self._stdin: IO[bytes] = self._process.stdin  # type: ignore
        self._stdout: IO[bytes] | None = None
        self._stderr: IO[bytes] | None = None
        self._stdout_reader_thread: threading.Thread | None = None
        self._stderr_reader_thread: threading.Thread | None = None

        if self.buffer:
            n = f"popen-stdout-reader:pid-{self._process.pid}"
            self._stdout = self._process.stdout
            _args = (self._stdout, self.buffer)
            self._stdout_reader_thread = threading.Thread(
                target=self._pipe_reader, args=_args, daemon=True, name=n
            )
            self._stdout_reader_thread.start()

        if piping_stderr:
            n = f"popen-stderr-reader:pid-{self._process.pid}"
            self._stderr = self._process.stderr
            _args = (self._stderr, stderr)
            self._stderr_reader_thread = threading.Thread(
                target=self._pipe_reader, args=_args, daemon=True, name=n
            )
            self._stderr_reader_thread.start()

    @staticmethod
    def _on_error(_self: FFmpegSink, error: Exception, data: VoiceData | None) -> None:
        _self.client.stop_recording()  # type: ignore

    def is_opus(self) -> bool:
        return False

    def cleanup(self) -> None:
        self._kill_processes()
        self._process = self._stdout = self._stdin = self._stderr = MISSING

    def write(self, user: User | Member | None, data: VoiceData) -> None:
        if self._process and not self._stdin.closed:
            audio = data.opus if self.is_opus() else data.pcm
            assert audio is not None

            try:
                self._stdin.write(audio)
            except Exception as exc:
                _log.exception("Error while writing audio data to stdin ffmpeg")
                self._kill_processes()
                self.on_error(self, exc, data)

    def to_file(
        self, filename: str, /, *, description: str | None = None, spoiler: bool = False
    ) -> File | None:
        """Returns the :class:`discord.File` of this sink.

        This is only applicable if this sink uses a ``buffer`` instead of a ``filename``.

        .. warning::

            This should be used only after the sink has stopped recording.
        """
        if self.buffer is not MISSING:
            fp = File(
                self.buffer.read(),
                filename=filename,
                description=description,
                spoiler=spoiler,
            )
            return fp
        return None

    def _spawn_process(self, args: Any, **subprocess_kwargs: Any) -> subprocess.Popen:
        _log.debug(
            "Spawning ffmpeg process with command %s and kwargs %s",
            args,
            subprocess_kwargs,
        )
        process = None

        try:
            process = subprocess.Popen(
                args, creationflags=CREATE_NO_WINDOW, **subprocess_kwargs
            )
        except FileNotFoundError:
            executable = args.partition(" ")[0] if isinstance(args, str) else args[0]
            raise FFmpegNotFound(f"{executable!r} executable was not found") from None
        except subprocess.SubprocessError as exc:
            raise Exception(f"Popen failed: {exc.__class__.__name__}: {exc}") from exc
        else:
            return process

    def _kill_processes(self) -> None:
        proc: subprocess.Popen = getattr(self, "_process", MISSING)

        if proc is MISSING:
            return

        _log.debug("Terminating ffmpeg process %s", proc.pid)

        try:
            self._stdin.close()
        except Exception:
            pass

        _log.debug("Waiting for ffmpeg process %s", proc.pid)

        try:
            proc.wait(5)
        except Exception:
            pass

        try:
            proc.kill()
        except Exception as exc:
            _log.exception(
                "Ignoring exception while killing Popen process %s",
                proc.pid,
                exc_info=exc,
            )

        if proc.poll() is None:
            _log.info(
                "ffmpeg process %s has not terminated. Waiting to terminate...",
                proc.pid,
            )
            proc.communicate()
            _log.info(
                "ffmpeg process %s should have terminated with a return code of %s",
                proc.pid,
                proc.returncode,
            )
        else:
            _log.info(
                "ffmpeg process %s successfully terminated with return code of %s",
                proc.pid,
                proc.returncode,
            )

        self._process = MISSING

    def _pipe_reader(self, source: IO[bytes], dest: IO[bytes]) -> None:
        while self._process:
            if source.closed:
                return

            try:
                data = source.read(FFmpegAudio.BLOCKSIZE)
            except (OSError, ValueError) as exc:
                _log.debug("FFmpeg stdin pipe closed with exception %s", exc)
                return
            except Exception:
                _log.debug(
                    "An error ocurred in %s, this can be ignored", self, exc_info=True
                )
                return

            if data is None:
                return

            try:
                dest.write(data)
            except Exception as exc:
                _log.exception(
                    "Error while writing to destination pipe %s", self, exc_info=exc
                )
                self._kill_processes()
                self.on_error(self, exc, None)
                return


class FilterSink(Sink):
    r"""A sink that calls filtering callbacks before writing.

    .. versionadded:: 2.7

    Parameters
    ----------
    destination: :class:`Sink`
        The sink that is being filtered.
    filters: Sequence[Callable[[:class:`User` | :class`Member` | :data:`None`, :class:`VoiceData`], :class:`bool`]]
        The filters of this sink.
    filtering_mode: Literal["all", "any"]
        How the filters should work, if ``all`, all filters must be successful in order for
        a voice data packet to be written. Using ``any`` will make it so only one filter is
        required to be successful in order for a voice data packet to be written.
    """

    def __init__(
        self,
        destination: Sink,
        filters: Sequence[Callable[[User | Member | None, VoiceData], bool]],
        *,
        filtering_mode: Literal["all", "any"] = "all",
    ) -> None:
        if not filters:
            raise ValueError("filters must have at least one callback")

        if not isinstance(destination, SinkBase):
            raise TypeError(
                f"expected a Sink object, got {destination.__class__.__name__}"
            )

        self._filter_strat = all if filtering_mode == "all" else any
        self.filters: Sequence[Callable[[User | Member | None, VoiceData], bool]] = (
            filters
        )
        self.destination: Sink = destination
        super().__init__(dest=destination)

    def is_opus(self) -> bool:
        return self.destination.is_opus()

    def write(self, user: User | Member | None, data: VoiceData) -> None:
        if self._filter_strat(f(user, data) for f in self.filters):
            self.destination.write(user, data)

    def cleanup(self) -> None:
        self.filters = []
        self.destination.cleanup()
