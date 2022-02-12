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
import abc

from aiohttp import web


class SessionBase(abc.ABC):
    # Since this is an ABC class and all, it shouldn't be documented.
    def __init__(self, host, multicast_port, *, port=None):
        self.host = host
        self.port = port
        self.mcp = multicast_port

    @property
    def url(self):
        """The WebSocket URL."""
        return "ws://{0.host}:{1}".format(  # the url + port and stuff.
            self, self.port if self.port else self.multicast_port
        )


class ServerBase(abc.ABC):
    # also shouldn't be documented
    def __init__(self, host):
        self.host = host
        self.routes = {}
        self.endpoints = {}

    def route(self, name=None):
        """Used to register a coroutine as a endpoint
        with an instance of :class:`discord.ext.ipc.Server`

        .. versionadded:: 2.1
        """

        def decorator(func):
            """The decorator class allowing use of the function name.

            .. versionadded:: 2.1
            """
            if not name:
                self.endpoints[func.__name__] = func
            else:
                self.endpoints[name] = func
            return func

        return decorator

    def update_endpoints(self):
        """Updates the current endpoints

        .. versionadded:: 2.1
        """
        self.endpoints = {**self.endpoints, **self.routes}

        self.routes = {}  # mypy does not like this..

    async def _start(self, app, port):
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, self.host, port)
        await site.start()


class IPCServerResponseBase(abc.ABC):
    def __init__(self, data):
        self._json = data
        self.length = len(data)

        self.endpoint = data["endpoint"]

        for key, value in data["data"].items():
            setattr(self, key, value)
