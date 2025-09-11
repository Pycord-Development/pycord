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

import threading
from typing import Generic, TypeVar

T = TypeVar("T")


class MultiDataEvent(Generic[T]):
    """
    Something like the inverse of a Condition.  A 1-waiting-on-N type of object,
    with accompanying data object for convenience.
    """

    def __init__(self):
        self._items: list[T] = []
        self._ready: threading.Event = threading.Event()

    @property
    def items(self) -> list[T]:
        """A shallow copy of the currently ready objects."""
        return self._items.copy()

    def is_ready(self) -> bool:
        return self._ready.is_set()

    def _check_ready(self) -> None:
        if self._items:
            self._ready.set()
        else:
            self._ready.clear()

    def notify(self) -> None:
        self._ready.set()
        self._check_ready()

    def wait(self, timeout: float | None = None) -> bool:
        self._check_ready()
        return self._ready.wait(timeout)

    def register(self, item: T) -> None:
        self._items.append(item)
        self._ready.set()

    def unregister(self, item: T) -> None:
        try:
            self._items.remove(item)
        except ValueError:
            pass
        self._check_ready()

    def clear(self) -> None:
        self._items.clear()
        self._ready.clear()