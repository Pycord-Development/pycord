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

from __future__ import annotations # will probably need in future for type hinting

import asyncio
import inspect
from typing import Callable

from .client import Client
from .shard import AutoShardedClient
from .utils import get
from .commands import SlashCommand, MessageCommand, UserCommand

class ApplicationCommandMixin:
    def __init__(self):
        self.to_register = []
        self.app_commands = {}

    def add_application_command(self, command):
        self.to_register.append(command)

    def remove_application_command(self, command):
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
    def slash(self, **kwargs):
        def wrap(func: Callable) -> SlashCommand:
            command = SlashCommand(func, **kwargs)
            self.add_application_command(command)
            return command

        return wrap

    command = slash


class Bot(BotBase, Client):


class AutoShardedBot(BotBase, AutoShardedClient):
    pass
