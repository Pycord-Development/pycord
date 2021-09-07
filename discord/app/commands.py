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

import asyncio
import inspect
from collections import OrderedDict
from typing import Callable, Dict, List, Optional, Union

from ..enums import SlashCommandOptionType
from ..member import Member
from ..user import User
from ..message import Message
from .context import InteractionContext
from ..utils import find, get_or_fetch
from ..errors import NotFound


class ApplicationCommand:
    def __repr__(self):
        return f"<discord.app.commands.{self.__class__.__name__} name={self.name}>"

    def __eq__(self, other):
        return isinstance(other, self.__class__)


class SlashCommand(ApplicationCommand):
    type = 1

    def __new__(cls, *args, **kwargs) -> SlashCommand:
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self

    def __init__(self, func: Callable, *args, **kwargs) -> None:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine.")
        self.callback = func

        self.guild_ids: Optional[List[int]] = kwargs.get("guild_ids", None)

        name = kwargs.get("name") or func.__name__
        if not isinstance(name, str):
            raise TypeError("Name of a command must be a string.")
        self.name: str = name

        description = kwargs.get("description") or (
            inspect.cleandoc(func.__doc__).splitlines()[0]
            if func.__doc__ is not None
            else "No description provided"
        )

        if not isinstance(description, str):
            raise TypeError("Description of a command must be a string.")
        self.description: str = description
        self.is_subcommand: bool = False

        params = OrderedDict(inspect.signature(self.callback).parameters)
        self.options = self.parse_options(params)

    def parse_options(self, params: OrderedDict) -> List[Option]:
        final_options = []

        # Remove ctx, this needs to refactored when used in Cogs
        params.pop(list(params)[0]) 

        final_options = []
        
        for p_name, p_obj in params.items():

            option = p_obj.annotation
            if option == inspect.Parameter.empty:
                option = str
            
            if self._is_typing_optional(option):
                option = Option(option.__args__[0], "No description provided", required=False)

            if not isinstance(option, Option):
                option = Option(option, "No description provided")
                if p_obj.default != inspect.Parameter.empty:
                    option.required = False
                
            option.default = option.default or p_obj.default

            if option.default == inspect.Parameter.empty:
                option.default = None

            if option.name is None:
                option.name = p_name
                
            final_options.append(option)

        return final_options

        
    def _is_typing_optional(self, annotation):
        return getattr(annotation, "__origin__", None) is Union and type(None) in annotation.__args__  # type: ignore

    def to_dict(self) -> Dict:
        as_dict = {
            "name": self.name,
            "description": self.description,
            "options": [o.to_dict() for o in self.options],
        }
        if self.is_subcommand:
            as_dict["type"] = SlashCommandOptionType.sub_command.value

        return as_dict

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, SlashCommand)
            and other.name == self.name
            and other.description == self.description
        )

    async def invoke(self, ctx: InteractionContext) -> None:
        # TODO: Parse the args better, apply custom converters etc.
        kwargs = {}
        for arg in ctx.interaction.data.get("options", []):
            op = find(lambda x: x.name == arg["name"], self.options)
            arg = arg["value"]

            # Checks if input_type is user, role or channel
            if (
                SlashCommandOptionType.user.value
                <= op.input_type.value
                <= SlashCommandOptionType.role.value
            ):
                name = "member" if op.input_type.name == "user" else op.input_type.name
                arg = await get_or_fetch(ctx.guild, name, int(arg))

            elif op.input_type == SlashCommandOptionType.mentionable:
                try:
                    arg = await get_or_fetch(ctx.guild, "member", int(arg))
                except NotFound:
                    arg = await get_or_fetch(ctx.guild, "role", int(arg))

            kwargs[op.name] = arg

        for o in self.options:
            if o.name not in kwargs:
                kwargs[o.name] = o.default
        await self.callback(ctx, **kwargs)


class Option:
    def __init__(
        self, input_type, /, description: str, **kwargs
    ) -> None:
        self.name: Optional[str] = kwargs.pop("name", None)
        self.description = description
        if not isinstance(input_type, SlashCommandOptionType):
            input_type = SlashCommandOptionType.from_datatype(input_type)
        self.input_type = input_type
        self.required: bool = kwargs.pop("required", True)
        self.choices: List[OptionChoice] = [
            o if isinstance(o, OptionChoice) else OptionChoice(o)
            for o in kwargs.pop("choices", list())
        ]
        self.default = kwargs.pop("default", None)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "type": self.input_type.value,
            "required": self.required,
            "choices": [c.to_dict() for c in self.choices],
        }

    def __repr__(self):
        return f"<discord.app.commands.{self.__class__.__name__} name={self.name}>"


class OptionChoice:
    def __init__(self, name: str, value: Optional[Union[str, int, float]] = None):
        self.name = name
        self.value = value or name

    def to_dict(self) -> Dict[str, Union[str, int, float]]:
        return {"name": self.name, "value": self.value}


class SubCommandGroup(Option):
    type = 1

    def __init__(
        self,
        name: str,
        description: str,
        guild_ids: Optional[List[int]] = None,
        parent_group: Optional[SubCommandGroup] = None,
    ) -> None:
        super().__init__(
            SlashCommandOptionType.sub_command_group,
            name=name,
            description=description,
        )
        self.subcommands: List[Union[SlashCommand, SubCommandGroup]] = []
        self.guild_ids = guild_ids
        self.parent_group = parent_group

    def to_dict(self) -> Dict:
        as_dict = {
            "name": self.name,
            "description": self.description,
            "options": [c.to_dict() for c in self.subcommands],
        }

        if self.parent_group is not None:
            as_dict["type"] = self.input_type.value

        return as_dict

    def command(self, **kwargs) -> SlashCommand:
        def wrap(func) -> SlashCommand:
            command = SlashCommand(func, **kwargs)
            command.is_subcommand = True
            self.subcommands.append(command)
            return command

        return wrap

    def command_group(self, name, description) -> SubCommandGroup:
        if self.parent_group is not None:
            # TODO: Improve this error message
            raise Exception("Subcommands can only be nested once")

        sub_command_group = SubCommandGroup(name, description, parent_group=self)
        self.subcommands.append(sub_command_group)
        return sub_command_group

    async def invoke(self, ctx: InteractionContext) -> None:
        option = ctx.interaction.data["options"][0]
        command = find(lambda x: x.name == option["name"], self.subcommands)
        ctx.interaction.data = option
        await command.invoke(ctx)


class UserCommand(ApplicationCommand):
    type = 2

    def __new__(cls, *args, **kwargs) -> UserCommand:
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self

    def __init__(self, func: Callable, *args, **kwargs) -> None:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine.")
        self.callback = func

        self.guild_ids: Optional[List[int]] = kwargs.get("guild_ids", None)

        self.description = (
            ""  # Discord API doesn't support setting descriptions for User commands
        )
        self.name: str = kwargs.pop("name", func.__name__)
        if not isinstance(self.name, str):
            raise TypeError("Name of a command must be a string.")

    def to_dict(self) -> Dict[str, Union[str, int]]:
        return {"name": self.name, "description": self.description, "type": self.type}

    async def invoke(self, ctx: InteractionContext) -> None:
        if "members" not in ctx.interaction.data["resolved"]:
            _data = ctx.interaction.data["resolved"]["users"]
            for i, v in _data.items():
                v["id"] = int(i)
                user = v
            target = User(state=ctx.interaction._state, data=user)
        else:
            _data = ctx.interaction.data["resolved"]["members"]
            for i, v in _data.items():
                v["id"] = int(i)
                member = v
            _data = ctx.interaction.data["resolved"]["users"]
            for i, v in _data.items():
                v["id"] = int(i)
                user = v
            member["user"] = user
            target = Member(
                data=member,
                guild=ctx.interaction._state._get_guild(ctx.interaction.guild_id),
                state=ctx.interaction._state,
            )
        await self.callback(ctx, target)


class MessageCommand(ApplicationCommand):
    type = 3

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self

    def __init__(self, func, *args, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine.")
        self.callback = func

        self.guild_ids = kwargs.get("guild_ids", None)

        self.description = ""
        self.name = kwargs.pop("name", func.__name__)
        if not isinstance(self.name, str):
            raise TypeError("Name of a command must be a string.")

    def to_dict(self):
        return {"name": self.name, "description": self.description, "type": self.type}

    async def invoke(self, ctx: InteractionContext):
        _data = ctx.interaction.data["resolved"]["messages"]
        for i, v in _data.items():
            v["id"] = int(i)
            message = v
        channel = ctx.interaction._state.get_channel(int(message["channel_id"]))
        if channel is None:
            data = await ctx.interaction._state.http.start_private_message(
                int(message["author"]["id"])
            )
            channel = ctx.interaction._state.add_dm_channel(data)

        target = Message(state=ctx.interaction._state, channel=channel, data=message)
        await self.callback(ctx, target)
