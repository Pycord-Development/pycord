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
from typing import Callable

from .client import AutoShardedClient, Client
from .utils import get


class SlashCommand:
    type = 1

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

        description = (
            kwargs.get("description")
            or inspect.cleandoc(func.__doc__)
            or "No description set"
        )
        if not isinstance(name, str):
            raise TypeError("Description of a command must be a string.")
        self.description = description

        self.callback = func

    def to_dict(self):
        return {"name": self.name, "description": self.description}

    def __eq__(self, other):
        return (
            isinstance(other, SlashCommand)
            and other.name == self.name
            and other.description == self.description
        )


class UserCommand:
    type = 2


class MessageCommand:
    type = 3


class ApplicationCommandMixin:
    def __init__(self):
        self.to_register = []
        self.app_commands = {}

    def add_command(self, command):
        self.to_register.append(command)

    def remove_command(self, command):
        self.app_commands.remove(command)

    async def sync_commands(self):
        to_add = [i for i in self.to_register] + [i for i in self.app_commands.values()]
        cmds = await self.http.bulk_upsert_global_commands(
            self.user.id,
            [i.to_dict() for i in self.to_register]
            + [i.to_dict() for i in self.app_commands.values()],
        )
        new_cmds = {}
        self.app_commands = {}
        for i in cmds:
            cmd = get(to_add, name=i["name"], description=i["description"], type=1)
            new_cmds[i["id"]] = cmd

    async def register_commands(self):
        if len(self.app_commands) == 0:
            return

        cmds = await self.http.bulk_upsert_global_commands(
            self.user.id, [i.to_dict() for i in self.to_register]
        )
        for i in cmds:
            cmd = get(
                self.to_register, name=i["name"], description=i["description"], type=1
            )
            self.app_commands[i["id"]] = cmd


class BotBase(ApplicationCommandMixin):  # To Insert: CogMixin
    # TODO I think
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)

    async def start(self, token, *, reconnect=True) -> None:
        await self.login(token)
        await self.connect(reconnect=reconnect)
        await self.register_commands()


class Bot(BotBase, Client):
    def slash(self, **kwargs):
        def wrap(func: Callable) -> SlashCommand:
            command = SlashCommand(func, **kwargs)
            self.add_application_command(command)
            return command

        return wrap

    command = slash


class AutoShardedBot(BotBase, AutoShardedClient):
    pass
