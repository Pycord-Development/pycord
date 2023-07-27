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

import asyncio
import gc
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator, Literal, cast

from .errors import DiscordException


class RateLimitException(DiscordException):
    ...


class GlobalRateLimit:
    def __init__(self, concurrency: int, per: float | int) -> None:
        self.concurrency: int = concurrency
        self.per: float | int = per

        self.current: int = self.concurrency
        self._processing: list[asyncio.Future] = []
        self.loop: asyncio.AbstractEventLoop | None = None
        self.pending_reset: bool = False

    async def __aenter__(self) -> "GlobalRateLimit":
        if not self.loop:
            self.loop = asyncio.get_running_loop()

        while self.current == 0:
            future = self.loop.create_future()
            self._processing.append(future)
            await future

        self.current -= 1

        if not self.pending_reset:
            self.pending_reset = True
            self.loop.call_later(self.per, self.reset)

        return self

    async def __aexit__(self, *_) -> None:
        ...

    def reset(self) -> None:
        current_time = time.time()
        self.reset_at = current_time + self.per
        self.current = self.concurrency

        for _ in range(self.concurrency):
            try:
                self._processing.pop().set_result(None)
            except IndexError:
                break

        if len(self._processing):
            self.pending_reset = True
            self.loop.call_later(self.per, self.reset)
        else:
            self.pending_reset = False


class Bucket:
    """Represents a Discord rate limiting bucket."""

    def __init__(self, bucket_id: str) -> None:
        self.id = bucket_id
        self._waiting_processing: asyncio.Queue[asyncio.Future[None]] = asyncio.Queue()
        self._processing: list[asyncio.Future] = []
        self._remaining: int | None = None

        self._experiencing_reset = asyncio.Event()

        self._uninitialized = asyncio.Event()

        self._uninitialized.set()
        self.no_metadata = False
        self.limit = None
        self._reset_after_known = False

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[None]:
        # if this bucket doesn't have a rate limit
        # just let every request pass
        if self.no_metadata:
            yield
            return

        # this assumes this is an older bucket
        if self._remaining is None and self.limit is not None:
            self._remaining = self.limit

        if self._remaining:
            fut = asyncio.Future()

            remaining_after = self._remaining - len(self._processing)

            if remaining_after <= 0:
                # don't have to care about waiting since this queue is unlimited
                self._waiting_processing.put_nowait(fut)
                await fut

            self._processing.append(fut)

            try:
                yield
            except:
                self._release(1)

                raise
            finally:
                self._processing.remove(fut)

            return

        fut = asyncio.Future()

        # if we don't have the bucket's metadata
        # we should let the user fire this request
        # and see what metadata we get from it.
        if self._uninitialized.is_set():
            self._uninitialized.clear()

            self._processing.append(fut)

            try:
                yield
            except:
                self._release(1)

                raise
            else:
                if self._remaining:
                    self._release(self._remaining)
                elif self.no_metadata:
                    self._release()
                else:
                    self._release(1)
            finally:
                self._processing.remove(fut)
                self._uninitialized.set()
            return

        await self._uninitialized.wait()

        # after initialization reacquire and try again
        async with self.acquire():
            yield

    def _release(self, count: int | None = None) -> None:
        if count:
            num = min(count, self._waiting_processing.qsize())
        else:
            num = self._waiting_processing.qsize()

        for _ in range(num):
            fut = self._waiting_processing.get_nowait()

            self._waiting_processing.task_done()

            fut.set_result(None)

    @property
    def garbage(self) -> bool:
        """Whether this bucket should be collected by the garbage collector."""

        # this bucket has futures reserved, do not collect yet
        if self._processing:
            return False

        # this bucket has no limit, it is garbage
        if self.no_metadata:
            return True

        # this bucket has yet to expire
        if self._remaining is not None:
            return False

        return False

    async def force_close(self) -> None:
        """Forcibly close this bucket from use."""

        for fut in self._processing:
            fut.set_exception(asyncio.CancelledError)

    def set_metadata(
        self,
        remaining: int | None = None,
        reset_after: int | None = None,
    ) -> None:
        if remaining is None and reset_after is None:
            self.no_metadata = True
            self._release()
        else:
            self._remaining = remaining

            if self._experiencing_reset.is_set():
                return

            self._experiencing_reset.set()

            loop = asyncio.get_running_loop()
            # NOTE: 0.5 is an offset to reset_after.
            # maybe fine tune to a more specific number?
            loop.call_later(cast(float, reset_after) + 0.5, self._reset)

    def _reset(self) -> None:
        self._experiencing_reset.clear()
        self._remaining = None

        self._release()


class BucketStorage:
    """A customizable, optionally replacable storage medium for buckets."""

    def __init__(self, global_concurrency: int = 10, per_concurrency: int = 60) -> None:
        self._buckets: dict[str, Bucket] = {}
        self.global_concurrency = GlobalRateLimit(per_concurrency, global_concurrency)

        gc.callbacks.append(self._collect_buckets)

    def _collect_buckets(
        self, phase: Literal["start", "stop"], info: dict[str, int]
    ) -> None:
        del info

        if phase == "stop":
            return

        for id, bucket in self._buckets.copy().items():
            if bucket.garbage:
                del self._buckets[id]

    async def append(self, id: str, bucket: Bucket) -> None:
        self._buckets[id] = bucket

    async def get(self, id: str) -> Bucket | None:
        return self._buckets.get(id)

    async def get_or_create(self, id: str) -> Bucket:
        return await self.get(id) or Bucket(id)


class DynamicBucket:
    def __init__(self) -> None:
        self.is_global: bool | None = None
        self._request_queue: asyncio.Queue[asyncio.Event] | None = None
        self.rate_limited: bool = False

    async def executed(
        self, reset_after: int | float, limit: int, is_global: bool
    ) -> None:
        self.rate_limited = True
        self.is_global = is_global
        self._reset_after = reset_after
        self._request_queue = asyncio.Queue()

        await asyncio.sleep(reset_after)

        self.is_global = False

        # NOTE: This could break if someone did a second global rate limit somehow
        requests_passed: int = 0
        for _ in range(self._request_queue.qsize() - 1):
            if requests_passed == limit:
                requests_passed = 0
                if not is_global:
                    await asyncio.sleep(reset_after)
                else:
                    await asyncio.sleep(5)

            requests_passed += 1
            e = await self._request_queue.get()
            e.set()

    async def wait(self) -> None:
        if not self.rate_limited:
            return

        event = asyncio.Event()

        if self._request_queue:
            self._request_queue.put_nowait(event)
        else:
            raise RateLimitException(
                "Request queue does not exist, rate limit may have been solved."
            )
        await event.wait()
