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
from typing import Callable, Union

from .client import Client
from .shard import AutoShardedClient

from .user import User
from .role import Role
from . import abc 
from .utils import get

class Option:
    option_types = {
        str: 3,
        int: 4,
        bool: 5,
        User: 6,
        abc.GuildChannel: 7,
        Role: 8,
        Union[Role, User]: 9,
        float: 10
    }

    def __init__(self, type_, name, description, required=None, choices=None):
        self.type = type_
        self.name = name
        self.description = description
        self.choices = choices
        self.required = required

    def to_dict(self):
        _data = {
            'type': Option.option_types[self.type],
            'name': self.name,
            'description': self.description,
            'required': self.required
        }
        if self.choices is not None:
            _data['choices'] = self.choices

        return _data

def get_options(callback):
    sig = inspect.signature(callback)
    options = []

    iterator = iter(sig.parameters.items())
    # Assuming that we want to pass some sort of Context/Interaction
    next(iterator)

    for name, param in iterator:
        option = Option(
            type_=param.annotation,
            name=name,
            # TODO: implement this properly
            description=name,
            required=param.default == inspect._empty
        )

        options.append(option)

    return options if options else None

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
        self.options = get_options(func)

    def to_dict(self):
        options = [option.to_dict() for option in self.options]
        return {"name": self.name, "description": self.description, 'options': options}

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
