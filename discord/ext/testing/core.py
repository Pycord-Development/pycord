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

import inspect
import json
import os
from typing import Any, Callable, Iterable, Literal, Sequence
from unittest.mock import AsyncMock, MagicMock, patch

from ... import MISSING, File
from ...client import Client
from ...http import HTTPClient, Route

__all__ = (
    "Test",
    "Mocked",
    "get_mock_response",
)


def get_mock_response(name: str) -> dict[str, Any]:
    with open(
        os.path.join(os.path.dirname(__file__), "mock_responses", f"{name}.json")
    ) as f:
        return json.load(f)


class Mocked:
    def __init__(
        self,
        name: str,
        return_value: Any | Callable[[...], Any] | None = None,
        approach: Literal["merge", "replace"] = "replace",
    ):
        self.name = name
        self.mock: MagicMock | AsyncMock | None = None

        if callable(return_value):

            async def wrapped(*args, **kwargs):
                inner = return_value(*args, **kwargs)
                if inspect.isawaitable(inner):
                    inner = await inner
                if approach == "merge":
                    inner = dict(**get_mock_response(self.name), **inner)
                return inner

            self.patcher = patch.object(HTTPClient, self.name, wrapped)
            self.return_value = None
        else:
            if return_value is None:
                return_value = {}
                approach = "merge"
            if approach == "merge":
                return_value = dict(**get_mock_response(self.name), **return_value)
            self.patcher = patch.object(HTTPClient, self.name, autospec=True)
            self.return_value = return_value

    def __enter__(self) -> MagicMock | AsyncMock:
        self.mock = self.patcher.start()
        if self.return_value is not None:

            async def _coro():
                return self.return_value

            self.mock.return_value = _coro()
        return self.mock

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.patcher.stop()


class Test:
    def __init__(self, client: Client):
        self.__client = client

    def patch(
        self,
        name: str,
        return_value: Any | Callable[[...], Any] | None = None,
        approach: Literal["merge", "replace"] = "replace",
    ) -> Mocked:
        return Mocked(name, return_value, approach)

    def makes_request(
        self,
        route: Route,
        *,
        files: Sequence[File] | None | MISSING = MISSING,
        form: Iterable[dict[str, Any]] | None | MISSING = MISSING,
        side_effect: Any | Callable[[...], Any] | None = None,
        **kwargs: Any,
    ):
        class _Request:
            def __init__(
                self, client: Client, route, files, form, *, side_effect, **kwargs
            ):
                if side_effect is None:
                    self.patcher = patch.object(client.http, "request", autospec=True)
                else:
                    self.patcher = patch.object(
                        client.http, "request", side_effect=side_effect
                    )
                self.route = route
                self.files = files
                self.form = form
                self.kwargs = kwargs

            def __enter__(self):
                self.mock = self.patcher.start()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.patcher.stop()
                if self.form is not MISSING:
                    self.kwargs["form"] = self.form
                if self.files is not MISSING:
                    self.kwargs["files"] = self.files
                self.mock.assert_called_once_with(
                    self.route,
                    **self.kwargs,
                )

        return _Request(
            self.__client, route, files, form, side_effect=side_effect, **kwargs
        )

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__client, name)
