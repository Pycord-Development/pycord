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

import functools
import random
from typing import Callable, TypedDict
from unittest.mock import MagicMock

import pytest

from discord import GatewayNotFound, HTTPException, Route
from discord.http import API_VERSION

from ..core import client


@pytest.fixture(params=(True, False))
def zlib(request) -> bool:
    return request.param


@pytest.fixture(params=(None,))
def encoding(request) -> str | None:
    return request.param


class GetGateway(TypedDict):
    url: str


class GetBotGateway(TypedDict):
    url: str
    shards: int


get_gateway_val = GetGateway(url="test")  # TODO: Make gateway url random


@pytest.fixture(params=(get_gateway_val, None))
def mocked_get_gateway(request) -> Callable[[], GetGateway] | HTTPException:
    mock = MagicMock()
    if (param := request.param) is None:
        return HTTPException(mock, "Error")
    return lambda *args: param


@pytest.fixture
def mocked_get_bot_gateway(
    mocked_get_gateway,
) -> Callable[[], GetBotGateway] | HTTPException:
    if isinstance(mocked_get_gateway, HTTPException):
        return mocked_get_gateway

    cached_randint = functools.lru_cache(random.randint)

    return lambda *args: GetBotGateway(shards=cached_randint(1, 100), **get_gateway_val)


async def test_get_gateway(client, encoding, zlib, mocked_get_gateway) -> None:
    with client.makes_request(
        Route("GET", "/gateway"),
        side_effect=mocked_get_gateway,
    ):
        coro = client.http.get_gateway(encoding=encoding, zlib=zlib)
        if isinstance(mocked_get_gateway, HTTPException):
            with pytest.raises(GatewayNotFound):
                await coro
        else:
            value = await coro
            mocked = mocked_get_gateway()
            expected = f"{mocked['url']}?encoding={encoding}&v={API_VERSION}"
            if zlib:
                expected += "&compress=zlib-stream"
            assert value == expected


async def test_get_bot_gateway(client, encoding, zlib, mocked_get_bot_gateway) -> None:
    with client.makes_request(
        Route("GET", "/gateway/bot"),
        side_effect=mocked_get_bot_gateway,
    ):
        coro = client.http.get_bot_gateway(encoding=encoding, zlib=zlib)
        if isinstance(mocked_get_bot_gateway, HTTPException):
            with pytest.raises(GatewayNotFound):
                await coro
        else:
            value = await coro
            mocked = mocked_get_bot_gateway()
            url = f"{mocked['url']}?encoding={encoding}&v={API_VERSION}"
            if zlib:
                url += "&compress=zlib-stream"
            expected = (mocked["shards"], url)
            assert value == expected
