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
import inspect

from .client import *


class ApplicationCommand:
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self

    def __init__(self, func, *args, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine.")

        name = kwargs.get("name") or func.__name__
        if not isinstance(name, str):
            raise TypeError("Name of a command must be a string.")
        self.name = name

        description = kwargs.get("description") or inspect.cleandoc(func.__doc__)
        if not isinstance(description, str):
            raise TypeError("Description of a command must be a string.")
        self.description = description

        self.callback = func

    def to_dict(self):
        return {"name": self.name, "description": self.description}


class ApplicationMixin:
    def __init__(self):
        self.application_commands = []

    def add_application_command(self, command):
        self.application_commands.append(command)

    async def register_application_commands(self):
        if len(self.application_commands) == 0:
            return
        await self.http.bulk_upsert_global_commands(
            self.user.id, [i.to_dict() for i in self.application_commands]
        )


class BotBase(ApplicationMixin):
    pass


class Bot(BotBase, Client):
    def interaction_command(self, **kwargs):
        def wrap(func: function) -> ApplicationCommand:
            command = ApplicationCommand(func, **kwargs)
            self.add_application_command(command)
            return command

        return wrap

    command = slash = interaction_command


class AutoShardedBot(BotBase, Client):
    pass
