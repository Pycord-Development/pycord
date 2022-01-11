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
import logging
import typing

import aiohttp

from discord import utils

# library stub error.
from ...errors import ConnectionClosed  # type: ignore
from .base import SessionBase

_log = logging.getLogger(__name__)


class Session(SessionBase):
    """The session interacting with the :class:`Server`

    .. versionadded:: 2.0

    Attributes
    ----------
    bot :class:`Union`
        The current bot process
    host
        The host to send requests to
    mcp
        The multicast port to connect to
    token
        The secret token to provide to the Server
    port
        The port to connect to
    """

    def __init__(
        self,
        host,
        multicast_port,
        token,
        port=None,
    ):
        self.host = host
        self.mcp = multicast_port
        self.port = port
        self.token = token
        super().__init__(self.host, self.mcp, self.port)

    async def identify(self):
        self.__session = aiohttp.ClientSession()
        if not self.port:
            self.req = await self.__session.ws_connect(self.url, autoping=False)
            payload = {"connect": True, "headers": {"Authorization": self.token}}
            await self.req.send_json(payload, dumps=utils._to_json)
            received = await self.req.receive()
            if received.type in {aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED}:
                _log.error("Session was unexpectedly closed...")
                raise ConnectionClosed("Session was closed.")

            port_d = received.json(loads=utils._from_json)
            self.port = port_d["port"]
        self.reqr = await self.__session.ws_connect(
            self.url, autoclose=False, autoping=False
        )
        _log.debug(f"Initialized connection with {self.url}")

        return self.reqr

    async def request(self, endpoint, **kwargs):
        if not self.__session:
            self.identify()

        payload = {
            "endpoint": endpoint,
            "data": kwargs,
            "headers": {"Authorization": self.token},
        }
        _log.debug(f"Sending {payload}")
        await self.reqr.send_json(payload, dumps=utils._to_json)
        data = await self.reqr.receive()
        _log.debug(f"Recieved {data}")

        if data.type == aiohttp.WSMsgType.PING:
            _log.debug("Server has requested to ping, doing that now.")

            await self.reqr.ping()
        if data.type == aiohttp.WSMsgType.PONG:
            _log.debug("Given a pong by the server, requesting request again...")
            self.request(endpoint, **kwargs)

        if data.type == aiohttp.WSMsgType.CLOSED:
            _log.error("Connection was closed, Retrying connection now...")
            await self.__session.close()
            await asyncio.sleep(4)
            await self.identify()
            return await self.request(endpoint, **kwargs)

        return data.json(loads=utils._from_json)
