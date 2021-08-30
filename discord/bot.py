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
from .app import SlashCommand, SubCommandGroup, MessageCommand, UserCommand

class ApplicationCommandMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
            cmd = get(to_add, name=i["name"], description=i["description"], type=i["type"])
            new_cmds[i["id"]] = cmd

    async def register_commands(self):
        """|coro|
        Needs documentation

        By default, this coroutine is called inside the :func:`.on_connect`
        event. If you choose to override the :func:`.on_connect` event, then
        you should invoke this coroutine as well.
        """
        commands = []

        registered_commands = await self.http.get_global_commands(self.user.id)
        for command in [cmd for cmd in self.to_register if cmd.guild_ids is None]:
            as_dict = command.to_dict()
            if not len(registered_commands) == 0:
                matches = [x for x in registered_commands if x["name"] == command.name and x['type'] == command.type]
                # TODO: rewrite this, it seems inefficient
                if len(matches) > 0:
                    as_dict['id'] = matches[0]["id"]
            commands.append(as_dict)

        update_guild_commands = {}
        for command in [cmd for cmd in self.to_register if cmd.guild_ids is not None]:
            as_dict = command.to_dict()
            for guild_id in command.guild_ids:
                to_update = update_guild_commands.get(guild_id, [])
                update_guild_commands[guild_id] = to_update + [as_dict]

        for guild_id in update_guild_commands:
            cmds = await self.http.bulk_upsert_guild_commands(self.user.id, guild_id, update_guild_commands[guild_id])
            for i in cmds:
                cmd = get(self.to_register, name=i["name"], description=i["description"], type=i['type'])
                self.app_commands[i["id"]] = cmd

        cmds = await self.http.bulk_upsert_global_commands(self.user.id, commands)

        for i in cmds:
            cmd = get(
                self.to_register, name=i["name"], description=i["description"], type=i['type']
            )
            self.app_commands[i["id"]] = cmd

    async def handle_interaction(self, interaction):
        """|coro|
        Needs documentation

        By default, this coroutine is called inside the :func:`.on_interaction`
        event. If you choose to override the :func:`.on_interaction` event, then
        you should invoke this coroutine as well.
        """
        try:
            command = self.app_commands[interaction.data["id"]]
        except KeyError:
            print(f"Received unknown application command: {interaction.data}")
            await interaction.response.send_message("I didn't recognize that command")
        else:
            await command.invoke(interaction)


class BotBase(ApplicationCommandMixin):  # To Insert: CogMixin
    # TODO I think
    # def __init__(self, *args, **kwargs):
    #     super(Client, self).__init__(*args, **kwargs)

    async def on_connect(self):
        await self.register_commands()

    async def on_interaction(self, interaction):
        await self.handle_interaction(interaction)

    def slash(self, **kwargs):
        def wrap(func: Callable) -> SlashCommand:
            if isinstance(func, (UserCommand, MessageCommand)):
                func = func.callback
            elif callable(func) == False:
                raise TypeError("func needs to be a callable, UserCommand, or MessageCommand object.")

            command = SlashCommand(func, **kwargs)
            self.add_application_command(command)
            return command

        return wrap

    def app_user(self, **kwargs):
        def wrap(func: Callable) -> UserCommand:
            if isinstance(func, (SlashCommand, MessageCommand)):
                func = func.callback
            elif callable(func) == False:
                raise TypeError("func needs to be a callable, SlashCommand, or MessageCommand object.")

            command = UserCommand(func, **kwargs)
            self.add_application_command(command)
            return command

        return wrap

    def command_group(self, name, description, guild_ids=None):
        group = SubCommandGroup(name, description, guild_ids)
        self.add_application_command(group)
        return group

    @property
    def command(self):
        return self.slash


class Bot(BotBase, Client):
    pass

class AutoShardedBot(BotBase, AutoShardedClient):
    pass
