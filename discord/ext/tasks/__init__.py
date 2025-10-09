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
import inspect
import logging
import sys
import traceback
from collections.abc import Sequence
from typing import Any, Awaitable, Callable, Generic, TypeVar

import aiohttp

import discord
from discord.backoff import ExponentialBackoff
from discord.utils import MISSING

__all__ = ("loop",)

T = TypeVar("T")
_func = Callable[..., Awaitable[Any]]
_log = logging.getLogger(__name__)
LF = TypeVar("LF", bound=_func)
FT = TypeVar("FT", bound=_func)
ET = TypeVar("ET", bound=Callable[[Any, BaseException], Awaitable[Any]])


def is_ambiguous(dt: datetime.datetime) -> bool:
    if dt.tzinfo is None or isinstance(dt.tzinfo, datetime.timezone):
        return False

    before = dt.replace(fold=0)
    after = dt.replace(fold=1)

    same_offset = before.utcoffset() == after.utcoffset()
    same_dst = before.dst() == after.dst()
    return not (same_offset and same_dst)


def is_imaginary(dt: datetime.datetime) -> bool:
    if dt.tzinfo is None or isinstance(dt.tzinfo, datetime.timezone):
        return False

    tz = dt.tzinfo
    dt = dt.replace(tzinfo=None)
    roundtrip = (
        dt.replace(tzinfo=tz)
        .astimezone(datetime.timezone.utc)
        .astimezone(tz)
        .replace(tzinfo=None)
    )
    return dt != roundtrip


class SleepHandle:
    __slots__ = ("future", "loop", "handle")

    def __init__(
        self, dt: datetime.datetime, *, loop: asyncio.AbstractEventLoop
    ) -> None:
        self.loop: asyncio.AbstractEventLoop = loop
        self.future: asyncio.Future[None] = loop.create_future()
        relative_delta = discord.utils.compute_timedelta(dt)
        self.handle = loop.call_later(relative_delta, self._safe_result, self.future)

    @staticmethod
    def _safe_result(future: asyncio.Future) -> None:
        if not future.done():
            future.set_result(None)

    def recalculate(self, dt: datetime.datetime) -> None:
        self.handle.cancel()
        relative_delta = discord.utils.compute_timedelta(dt)
        self.handle = self.loop.call_later(
            relative_delta, self._safe_result, self.future
        )

    def wait(self) -> asyncio.Future[Any]:
        return self.future

    def done(self) -> bool:
        return self.future.done()

    def cancel(self) -> None:
        self.handle.cancel()
        self.future.cancel()


class Loop(Generic[LF]):
    """A background task helper that abstracts the loop and reconnection logic for you.

    The main interface to create this is through :func:`loop`.
    """

    def __init__(
        self,
        coro: LF,
        seconds: float,
        hours: float,
        minutes: float,
        time: datetime.time | Sequence[datetime.time],
        count: int | None,
        reconnect: bool,
        loop: asyncio.AbstractEventLoop | None,
        create_loop: bool,
        name: str | None,
    ) -> None:
        self.coro: LF = coro
        self.reconnect: bool = reconnect

        if create_loop is True and loop is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()

        self.loop: asyncio.AbstractEventLoop | None = loop

        self.name: str = (
            f"pycord-ext-task ({id(self):#x}): {coro.__qualname__}"
            if name in (None, MISSING)
            else name
        )
        self.count: int | None = count
        self._current_loop = 0
        self._handle: SleepHandle = MISSING
        self._task: asyncio.Task[None] = MISSING
        self._injected = None
        self._valid_exception = (
            OSError,
            discord.GatewayNotFound,
            discord.ConnectionClosed,
            aiohttp.ClientError,
            asyncio.TimeoutError,
        )
        self._create_loop = create_loop

        self._before_loop = None
        self._after_loop = None
        self._before_loop_running = False
        self._after_loop_running = False
        self._is_being_cancelled = False
        self._has_failed = False
        self._stop_next_iteration = False

        if self.count is not None and self.count <= 0:
            raise ValueError("count must be greater than 0 or None.")

        self.change_interval(seconds=seconds, minutes=minutes, hours=hours, time=time)
        self._last_iteration_failed = False
        self._last_iteration: datetime.datetime = MISSING
        self._next_iteration = None

        if not inspect.iscoroutinefunction(self.coro):
            raise TypeError(
                f"Expected coroutine function, not {type(self.coro).__name__!r}."
            )

        if loop is None and not create_loop:
            discord.Client._pending_loops.add_loop(self)

    async def _call_loop_function(self, name: str, *args: Any, **kwargs: Any) -> None:
        coro = getattr(self, f"_{name}")
        if coro is None:
            return

        if name.endswith("_loop"):
            setattr(self, f"_{name}_running", True)

        if self._injected is not None:
            await coro(self._injected, *args, **kwargs)
        else:
            await coro(*args, **kwargs)

        if name.endswith("_loop"):
            setattr(self, f"_{name}_running", False)

    def _try_sleep_until(self, dt: datetime.datetime):
        self._handle = SleepHandle(dt=dt, loop=asyncio.get_running_loop())
        return self._handle.wait()

    def _rel_time(self) -> bool:
        return self._time is MISSING

    def _expl_time(self) -> bool:
        return self._time is not MISSING

    async def _loop(self, *args: Any, **kwargs: Any) -> None:
        backoff = ExponentialBackoff()
        await self._call_loop_function("before_loop")
        self._last_iteration_failed = False
        if self._expl_time():
            self._next_iteration = self._get_next_sleep_time()
        else:
            self._next_iteration = datetime.datetime.now(datetime.timezone.utc)

        try:
            if self._stop_next_iteration:
                return

            while True:
                if self._expl_time():
                    await self._try_sleep_until(self._next_iteration)
                if not self._last_iteration_failed:
                    self._last_iteration = self._next_iteration
                    self._next_iteration = self._get_next_sleep_time()

                    while (
                        self._expl_time()
                        and self._next_iteration <= self._last_iteration
                    ):
                        _log.warning(
                            "Task %s woke up at %s, which was before expected (%s). Sleeping again to fix it...",
                            self.coro.__name__,
                            discord.utils.utcnow(),
                            self._next_iteration,
                        )
                        await self._try_sleep_until(self._next_iteration)
                        self._next_iteration = self._get_next_sleep_time()
                try:
                    await self.coro(*args, **kwargs)
                    self._last_iteration_failed = False
                except self._valid_exception as exc:
                    self._last_iteration_failed = True
                    if not self.reconnect:
                        raise

                    delay = backoff.delay()
                    _log.warning(
                        "Received an exception which was in the valid exception set. Task will run again in %.2f seconds",
                        self.coro.__name__,
                        delay,
                        exc_info=exc,
                    )
                    await asyncio.sleep(delay)
                else:
                    if self._stop_next_iteration:
                        return

                    if self._rel_time():
                        await self._try_sleep_until(self._next_iteration)

                    self._current_loop += 1
                    if self._current_loop == self.count:
                        break

        except asyncio.CancelledError:
            self._is_being_cancelled = True
            raise
        except Exception as exc:
            self._has_failed = True
            await self._call_loop_function("error", exc)
            raise exc
        finally:
            await self._call_loop_function("after_loop")
            if self._handle:
                self._handle.cancel()
            self._is_being_cancelled = False
            self._current_loop = 0
            self._stop_next_iteration = False
            self._has_failed = False

    def __get__(self, obj: T, objtype: type[T]) -> Loop[LF]:
        if obj is None:
            return self

        copy: Loop[LF] = Loop(
            self.coro,
            seconds=self._seconds,
            hours=self._hours,
            minutes=self._minutes,
            time=self._time,
            count=self.count,
            reconnect=self.reconnect,
            name=self.name,
            loop=self.loop,
            create_loop=self._create_loop,
        )
        copy._injected = obj
        copy._before_loop = self._before_loop
        copy._after_loop = self._after_loop
        copy._error = self._error
        setattr(obj, self.coro.__name__, copy)
        return copy

    @property
    def seconds(self) -> float | None:
        """Read-only value for the number of seconds
        between each iteration. ``None`` if an explicit ``time`` value was passed instead.

        .. versionadded:: 2.0
        """
        if self._seconds is not MISSING:
            return self._seconds

    @property
    def minutes(self) -> float | None:
        """Read-only value for the number of minutes
        between each iteration. ``None`` if an explicit ``time`` value was passed instead.

        .. versionadded:: 2.0
        """
        if self._minutes is not MISSING:
            return self._minutes

    @property
    def hours(self) -> float | None:
        """Read-only value for the number of hours
        between each iteration. ``None`` if an explicit ``time`` value was passed instead.

        .. versionadded:: 2.0
        """
        if self._hours is not MISSING:
            return self._hours

    @property
    def time(self) -> list[datetime.time] | None:
        """Read-only list for the exact times this loop runs at.
        ``None`` if relative times were passed instead.

        .. versionadded:: 2.0
        """
        if self._time is not MISSING:
            return self._time.copy()

    @property
    def current_loop(self) -> int:
        """The current iteration of the loop."""
        return self._current_loop

    @property
    def next_iteration(self) -> datetime.datetime | None:
        """When the next iteration of the loop will occur.

        .. versionadded:: 1.3
        """
        if self._task is MISSING:
            return None
        elif self._task and self._task.done() or self._stop_next_iteration:
            return None
        return self._next_iteration

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        r"""|coro|

        Calls the internal callback that the task holds.

        .. versionadded:: 1.6

        Parameters
        ------------
        \*args
            The arguments to use.
        \*\*kwargs
            The keyword arguments to use.
        """

        if self._injected is not None:
            args = (self._injected, *args)

        return await self.coro(*args, **kwargs)

    def start(self, *args: Any, **kwargs: Any) -> asyncio.Task[None] | None:
        r"""Starts the internal task in the event loop.

        Parameters
        ------------
        \*args
            The arguments to use.
        \*\*kwargs
            The keyword arguments to use.

        Raises
        --------
        RuntimeError
            A task has already been launched and is running.

        Returns
        ---------
        :class:`asyncio.Task`
            The task that has been created.
        """

        if self.loop is None:
            _log.warning(
                f"The task {self.name} has been set to be bound to a discord.Client instance, and will start running automatically "
                "when the client starts. If you want this task to be executed without it being bound to a discord.Client, "
                "set the create_loop parameter in the decorator to True, and don't forget to set the client.loop to the loop.loop"
            )
            return None

        if self._task is not MISSING and not self._task.done():
            raise RuntimeError("Task is already launched and is not completed.")

        if self._injected is not None:
            args = (self._injected, *args)

        self._task = asyncio.ensure_future(
            self.loop.create_task(self._loop(*args, **kwargs), name=self.name),
            loop=self.loop,
        )
        return self._task

    def stop(self) -> None:
        r"""Gracefully stops the task from running.

        Unlike :meth:`cancel`\, this allows the task to finish its
        current iteration before gracefully exiting.

        .. note::

            If the internal function raises an error that can be
            handled before finishing then it will retry until
            it succeeds.

            If this is undesirable, either remove the error handling
            before stopping via :meth:`clear_exception_types` or
            use :meth:`cancel` instead.

        .. versionadded:: 1.2
        """
        if self._task is not MISSING and not self._task.done():
            self._stop_next_iteration = True

    def _can_be_cancelled(self) -> bool:
        return bool(
            not self._is_being_cancelled and self._task and not self._task.done()
        )

    def cancel(self) -> None:
        """Cancels the internal task, if it is running."""
        if self._can_be_cancelled():
            self._task.cancel()

    def restart(self, *args: Any, **kwargs: Any) -> None:
        r"""A convenience method to restart the internal task.

        .. note::

            Due to the way this function works, the task is not
            returned like :meth:`start`.

        Parameters
        ------------
        \*args
            The arguments to use.
        \*\*kwargs
            The keyword arguments to use.
        """

        def restart_when_over(
            fut: Any, *, args: Any = args, kwargs: Any = kwargs
        ) -> None:
            self._task.remove_done_callback(restart_when_over)
            self.start(*args, **kwargs)

        if self._can_be_cancelled():
            self._task.add_done_callback(restart_when_over)
            self._task.cancel()

    def add_exception_type(self, *exceptions: type[BaseException]) -> None:
        r"""Adds exception types to be handled during the reconnect logic.

        By default, the exception types handled are those handled by
        :meth:`discord.Client.connect`\, which includes a lot of internet disconnection
        errors.

        This function is useful if you're interacting with a 3rd party library that
        raises its own set of exceptions.

        Parameters
        ------------
        \*exceptions: Type[:class:`BaseException`]
            An argument list of exception classes to handle.

        Raises
        --------
        TypeError
            An exception passed is either not a class or not inherited from :class:`BaseException`.
        """

        for exc in exceptions:
            if not inspect.isclass(exc):
                raise TypeError(f"{exc!r} must be a class.")
            if not issubclass(exc, BaseException):
                raise TypeError(f"{exc!r} must inherit from BaseException.")

        self._valid_exception = (*self._valid_exception, *exceptions)

    def clear_exception_types(self) -> None:
        """Removes all exception types that are handled.

        .. note::

            This operation obviously cannot be undone!
        """
        self._valid_exception = ()

    def remove_exception_type(self, *exceptions: type[BaseException]) -> bool:
        r"""Removes exception types from being handled during the reconnect logic.

        Parameters
        ------------
        \*exceptions: Type[:class:`BaseException`]
            An argument list of exception classes to handle.

        Returns
        ---------
        :class:`bool`
            Whether all exceptions were successfully removed.
        """
        old_length = len(self._valid_exception)
        self._valid_exception = tuple(
            x for x in self._valid_exception if x not in exceptions
        )
        return len(self._valid_exception) == old_length - len(exceptions)

    def get_task(self) -> asyncio.Task[None] | None:
        """Fetches the internal task or ``None`` if there isn't one running."""
        return self._task if self._task is not MISSING else None

    def is_being_cancelled(self) -> bool:
        """Whether the task is being cancelled."""
        return self._is_being_cancelled

    def failed(self) -> bool:
        """Whether the internal task has failed.

        .. versionadded:: 1.2
        """
        return self._has_failed

    def is_running(self) -> bool:
        """Check if the task is currently running.

        .. versionadded:: 1.4
        """
        return not bool(self._task.done()) if self._task is not MISSING else False

    async def _error(self, *args: Any) -> None:
        exception: Exception = args[-1]
        print(
            f"Unhandled exception in internal background task {self.coro.__name__!r}.",
            file=sys.stderr,
        )
        traceback.print_exception(
            type(exception), exception, exception.__traceback__, file=sys.stderr
        )

    def before_loop(self, coro: FT) -> FT:
        """A decorator that registers a coroutine to be called before the loop starts running.

        This is useful if you want to wait for some bot state before the loop starts,
        such as :meth:`discord.Client.wait_until_ready`.

        The coroutine must take no arguments (except ``self`` in a class context).

        Parameters
        ----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register before the loop runs.

        Raises
        ------
        TypeError
            The function was not a coroutine.
        """

        if not inspect.iscoroutinefunction(coro):
            raise TypeError(
                f"Expected coroutine function, received {coro.__class__.__name__!r}."
            )

        self._before_loop = coro
        return coro

    def after_loop(self, coro: FT) -> FT:
        """A decorator that register a coroutine to be called after the loop finished running.

        The coroutine must take no arguments (except ``self`` in a class context).

        .. note::

            This coroutine is called even during cancellation. If it is desirable
            to tell apart whether something was cancelled or not, check to see
            whether :meth:`is_being_cancelled` is ``True`` or not.

        Parameters
        ----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register after the loop finishes.

        Raises
        ------
        TypeError
            The function was not a coroutine.
        """

        if not inspect.iscoroutinefunction(coro):
            raise TypeError(
                f"Expected coroutine function, received {coro.__class__.__name__!r}."
            )

        self._after_loop = coro
        return coro

    def error(self, coro: ET) -> ET:
        """A decorator that registers a coroutine to be called if the task encounters an unhandled exception.

        The coroutine must take only one argument the exception raised (except ``self`` in a class context).

        By default, this prints to :data:`sys.stderr` however it could be
        overridden to have a different implementation.

        .. versionadded:: 1.4

        Parameters
        ----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register in the event of an unhandled exception.

        Raises
        ------
        TypeError
            The function was not a coroutine.
        """
        if not inspect.iscoroutinefunction(coro):
            raise TypeError(
                f"Expected coroutine function, received {coro.__class__.__name__!r}."
            )

        self._error = coro  # type: ignore
        return coro

    def _get_next_sleep_time(
        self, now: datetime.datetime = MISSING
    ) -> datetime.datetime:
        if self._sleep is not MISSING:
            return self._last_iteration + datetime.timedelta(seconds=self._sleep)

        if now is MISSING:
            now = datetime.datetime.now(datetime.timezone.utc)

        index = self._start_time_relative_to(now)

        if index is None:
            time = self._time[0]
            tomorrow = now.astimezone(time.tzinfo) + datetime.timedelta(days=1)
            date = tomorrow.date()
        else:
            time = self._time[index]
            date = now.astimezone(time.tzinfo).date()

        dt = datetime.datetime.combine(date, time, tzinfo=time.tzinfo)

        if dt.tzinfo is None or isinstance(dt.tzinfo, datetime.timezone):
            return dt

        if is_imaginary(dt):
            tomorrow = dt + datetime.timedelta(days=1)
            yesterday = dt - datetime.timedelta(days=1)
            return dt + (tomorrow.utcoffset() - yesterday.utcoffset())  # type: ignore
        elif is_ambiguous(dt):
            return dt.replace(fold=1)
        else:
            return dt

    def _start_time_relative_to(self, now: datetime.datetime) -> int | None:
        # now kwarg should be a datetime.datetime representing the time "now"
        # to calculate the next time index from

        # pre-condition: self._time is set
        for idx, time in enumerate(self._time):
            # Convert the current time to the target timezone
            # e.g. 18:00 UTC -> 03:00 UTC+9
            # Then compare the time instances to see if they're the same
            start = now.astimezone(time.tzinfo)
            if time >= start.timetz():
                return idx
        else:
            return None

    def _get_time_parameter(
        self,
        time: datetime.time | Sequence[datetime.time],
        *,
        dt: type[datetime.time] = datetime.time,
        utc: datetime.timezone = datetime.timezone.utc,
    ) -> list[datetime.time]:
        if isinstance(time, dt):
            inner = time if time.tzinfo is not None else time.replace(tzinfo=utc)
            return [inner]
        if not isinstance(time, Sequence):
            raise TypeError(
                "Expected datetime.time or a sequence of datetime.time for ``time``,"
                f" received {type(time)!r} instead."
            )
        if not time:
            raise ValueError("time parameter must not be an empty sequence.")

        ret: list[datetime.time] = []
        for index, t in enumerate(time):
            if not isinstance(t, dt):
                raise TypeError(
                    f"Expected a sequence of {dt!r} for ``time``, received"
                    f" {type(t).__name__!r} at index {index} instead."
                )
            ret.append(t if t.tzinfo is not None else t.replace(tzinfo=utc))

        return sorted(set(ret))  # de-dupe and sort times

    def change_interval(
        self,
        *,
        seconds: float = 0,
        minutes: float = 0,
        hours: float = 0,
        time: datetime.time | Sequence[datetime.time] = MISSING,
    ) -> None:
        """Changes the interval for the sleep time.

        .. versionadded:: 1.2

        Parameters
        ----------
        seconds: :class:`float`
            The number of seconds between every iteration.
        minutes: :class:`float`
            The number of minutes between every iteration.
        hours: :class:`float`
            The number of hours between every iteration.
        time: Union[:class:`datetime.time`, Sequence[:class:`datetime.time`]]
            The exact times to run this loop at. Either a non-empty list or a single
            value of :class:`datetime.time` should be passed.
            This cannot be used in conjunction with the relative time parameters.

            .. versionadded:: 2.0

            .. note::

                Duplicate times will be ignored, and only run once.

        Raises
        ------
        ValueError
            An invalid value was given.
        TypeError
            An invalid value for the ``time`` parameter was passed, or the
            ``time`` parameter was passed in conjunction with relative time parameters.
        """

        if time is MISSING:
            seconds = seconds or 0
            minutes = minutes or 0
            hours = hours or 0
            sleep = seconds + (minutes * 60.0) + (hours * 3600.0)
            if sleep < 0:
                raise ValueError("Total number of seconds cannot be less than zero.")

            self._sleep = sleep
            self._seconds = float(seconds)
            self._hours = float(hours)
            self._minutes = float(minutes)
            self._time: list[datetime.time] = MISSING
        else:
            if any((seconds, minutes, hours)):
                raise TypeError("Cannot mix explicit time with relative time")
            self._time = self._get_time_parameter(time)
            self._sleep = self._seconds = self._minutes = self._hours = MISSING

        if self.is_running() and self._last_iteration is not MISSING:
            self._next_iteration = self._get_next_sleep_time()
            if self._handle and not self._handle.done():
                # the loop is sleeping, recalculate based on new interval
                self._handle.recalculate(self._next_iteration)


def loop(
    *,
    seconds: float = MISSING,
    minutes: float = MISSING,
    hours: float = MISSING,
    time: datetime.time | Sequence[datetime.time] = MISSING,
    count: int | None = None,
    reconnect: bool = True,
    loop: asyncio.AbstractEventLoop | None = None,
    name: str | None = MISSING,
    create_loop: bool = False,
) -> Callable[[LF], Loop[LF]]:
    """A decorator that schedules a task in the background for you with
    optional reconnect logic. The decorator returns a :class:`Loop`.

    Parameters
    ----------
    seconds: :class:`float`
        The number of seconds between every iteration.
    minutes: :class:`float`
        The number of minutes between every iteration.
    hours: :class:`float`
        The number of hours between every iteration.
    time: Union[:class:`datetime.time`, Sequence[:class:`datetime.time`]]
        The exact times to run this loop at. Either a non-empty list or a single
        value of :class:`datetime.time` should be passed. Timezones are supported.
        If no timezone is given for the times, it is assumed to represent UTC time.

        This cannot be used in conjunction with the relative time parameters.

        .. note::

            Duplicate times will be ignored, and only run once.

        .. versionadded:: 2.0

    count: Optional[:class:`int`]
        The number of loops to do, ``None`` if it should be an
        infinite loop.
    reconnect: :class:`bool`
        Whether to handle errors and restart the task
        using an exponential back-off algorithm similar to the
        one used in :meth:`discord.Client.connect`.
    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The loop to use to register the task, defaults to ``None``.
    name: Optional[:class:`str`]
        The name to create the task with, defaults to ``None``.

        .. versionadded:: 2.7
    create_loop: :class:`bool`
        Whether this task should create their own event loop to start running it
        without a client bound to it.

        .. versionadded:: 2.7

    Raises
    ------
    ValueError
        An invalid value was given.
    TypeError
        The function was not a coroutine, an invalid value for the ``time`` parameter was passed,
        or ``time`` parameter was passed in conjunction with relative time parameters.
    """

    def decorator(func: LF) -> Loop[LF]:
        return Loop[LF](
            func,
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            count=count,
            time=time,
            reconnect=reconnect,
            name=name,
            loop=loop,
            create_loop=create_loop,
        )

    return decorator
