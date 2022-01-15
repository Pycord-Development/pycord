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
import logging

from aiohttp import web

from discord import utils

from .base import IPCServerResponseBase, ServerBase
from .errors import JSONEncodeError

_log = logging.getLogger(__name__)


class IPCServerResponse(IPCServerResponseBase):
    """The IPC Server Response

    .. versionadded:: 2.0
    """

    def to_json(self):
        return self._json

    def __repr__(self):
        return "<IPCServerResponse length={0.length}>".format(self)

    def __str__(self):
        return self.__repr__()


class Server(ServerBase):
    """The class which interacts with your :class:`Session`

    .. versionadded:: 2.0

    Attributes
    ----------
    host
        The url which the server is hosted
    routes
        The current routes
    endpoints
        The current endpoints
    """

    def __init__(
        self,
        host,
        token,
        bot,
        *,
        port=9956,
        multicast_connection=True,
        multicast_port=20000,
    ):
        self.bot = bot
        self.host = host
        self.token = token
        self.routes = {}
        self.endpoints = {}
        self.__mc_connect = multicast_connection
        self.mc_port = multicast_port
        self.loop = self.bot.loop
        self.port = port
        super().__init__(host)

    async def handle_request(self, request):
        """Handles a request sent from the :class:`Session`

        .. versionadded:: 2.0

        Attributes
        ----------
        ws
            The WebSocketResponse
        """
        self.update_endpoints()
        _log.info("Starting up IPC Server...")
        ws = web.WebSocketResponse()
        await ws.prepare(request)  # prepares the request.
        async for msg in ws:
            req = msg.json(utils._from_json)
            _log.debug(f"> {request}")
            endpoint = req.get("endpoint")
            headers = req.get("headers")
            if not headers or headers.get("Authorization") != self.token:
                _log.error("Request given has a invalid token")
                response = {"error": "Invalid token was provided", "code": 403}
            else:
                if not endpoint or endpoint not in self.endpoints:
                    _log.error("Request given has given an invalid endpoint")
                    response = {"error": "Invalid endpoint was provided", "code": 400}
                else:
                    s_r = IPCServerResponse(request)
                    try:
                        a_cls = self.bot.cogs.get(
                            self.endpoints[endpoint].__qualname__.split(".")[0]
                        )
                        if a_cls:
                            args = (a_cls, s_r)
                        else:
                            args = s_r
                    except AttributeError:
                        args = s_r
                    try:
                        response = await self.endpoints[endpoint](*args)
                    except Exception as exc:
                        _log.error(f"Exception with {endpoint} on {request}")
                        self.bot.dispatch("ipc_error", endpoint, request)
                        response = {"error": "Error was raised {exc}", "code": 500}
            try:
                await ws.send_json(response, dumps=utils._from_json)
                _log.debug(f"< {response}")
            except TypeError as exc:
                if str(exc).startswith("Object of type") and str(exc).endswith(
                    "is not JSON serializable"
                ):
                    _log.critical("Data sent is not able to be sent via sockets.")
                    await ws.send_json(
                        {
                            "error": "Data sent is not able to be sent via sockets.",
                            "code": 500,
                        }
                    )
                    raise JSONEncodeError(
                        "Data sent is not able to be sent via sockets."
                    )

    async def handle_multicast_request(self, request):
        """Handles a multicast request.

        .. versionadded:: 2.0
        """
        _log.info("Starting up IPC Multicast Server...")
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        async for msg in ws:
            recv = msg.json()
            headers = recv.get("headers")
            if not headers or headers.get("Authorization") != self.token:
                response = {"error": "Invalid token was provided", "code": 403}
            else:
                response = {
                    "message": f"Connection was successful, Welcome to {self.host}",
                    "port": self.port,
                    "code": 200,
                }
            _log.debug(f"< {response}")
            await ws.send_json(response)

    def run(self):
        """A blocking call used to start the Server function.

        Basically would be the same as: ::

            from aiohttp import web
            from discord.ext.ipc import Server

            server = web.Application()
            
            server.router.add_route("GET", "/", Server.handle_request)
            
            bot.loop.run_forever(self._start(server, "your_port"))
        
        with support for multicasting just changing one line, like so: ::

            # Instead of this
            server.router.add_route("GET", "/", Server.handle_request)
            # Do this
            server.router.add_route("GET", "/", Server.handle_multicast_request)
            # and also changing this
            bot.loop.run_forever(Server._start(server, "your_port"))
            # to this
            bot.loop.run_forever(Server._start(server, "multicast_port"))


        .. versionadded:: 2.0
        """
        self.bot.dispatch("ipc_ready")

        self.__server = web.Application()
        self.__server.router.add_route("GET", "/", self.handle_request)

        if self.__mc_connect:
            self._mc_server = web.Application()
            self._mc_server.router.add_route("GET", "/", self.handle_multicast_request)

            self.loop.run_forever(self._start(self._mc_server, self.mc_port))
        self.loop.run_forever(self._start(self.__server, self.port))
