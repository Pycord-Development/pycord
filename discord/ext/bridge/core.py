"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
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
from typing import Union, Any

import discord.commands.options
from discord.commands import Option, SlashCommand
from discord.enums import SlashCommandOptionType

from ..commands import AutoShardedBot as ExtAutoShardedBot
from ..commands import BadArgument
from ..commands import Bot as ExtBot
from ..commands import (
    Command,
    Converter,
    GuildChannelConverter,
    RoleConverter,
    UserConverter,
)

__all__ = ("BridgeCommand", "bridge_command", "BridgeExtCommand", "BridgeSlashCommand")

from ...utils import get


class BridgeSlashCommand(SlashCommand):
    """
    A subclass of :class:`.SlashCommand` that is used to implement bridge commands.
    """
    ...


class BridgeExtCommand(Command):
    """
    A subclass of :class:`.ext.commands.Command` that is used to implement bridge commands.
    """
    ...


class BridgeCommand:
    def __init__(self, callback, **kwargs):
        """
        This is the base class for commands that are compatible with both traditional (prefix-based) commands and slash
        commands.

        Parameters
        ----------
        callback: Callable[[BridgeContext, ...], Awaitable[Any]]
            The callback to invoke when the command is executed. The first argument will be a :class:`BridgeContext`,
            and any additional arguments will be passed to the callback. This callback must be a coroutine.
        kwargs: Optional[Dict[str, Any]]
            Keyword arguments that are directly passed to the respective command constructors.
        """
        self.callback = callback
        self.kwargs = kwargs

    def get_ext_command(self):
        """A method to get the ext.commands version of this command.

        Returns
        -------
        :class:`BridgeExtCommand`
            The respective traditional (prefix-based) version of the command.
        """
        command = BridgeExtCommand(self.callback, **self.kwargs)
        return command

    def get_application_command(self):
        """A method to get the discord.commands version of this command.

        Returns
        -------
        :class:`BridgeSlashCommand`
            The respective slash command version of the command.
        """
        command = BridgeSlashCommand(self.callback, **self.kwargs)
        return command

    def add_to(self, bot: Union[ExtBot, ExtAutoShardedBot]) -> None:
        """Adds the command to a bot.

        Parameters
        ----------
        bot: Union[:class:`ExtBot`, :class:`ExtAutoShardedBot`]
            The bot to add the command to.
        """
        bot.add_command(self.get_ext_command())
        bot.add_application_command(self.get_application_command())


def bridge_command(**kwargs):
    """A decorator that is used to wrap a function as a command.

    Parameters
    ----------
    kwargs: Optional[Dict[str, Any]]
        Keyword arguments that are directly passed to the respective command constructors.
    """

    def decorator(callback):
        return BridgeCommand(callback, **kwargs)

    return decorator


class MentionableConverter(Converter):
    """A converter that can convert a mention to a user or a role."""

    async def convert(self, ctx, argument):
        try:
            return await RoleConverter().convert(ctx, argument)
        except BadArgument:
            return await UserConverter().convert(ctx, argument)


def attachment_callback(*args):  # pylint: disable=unused-argument
    raise ValueError("Attachments are not supported for compatibility commands.")


class BridgeOption(Option, Converter):
    async def convert(self, ctx, argument) -> Any:
        if self.converter is not None:
            converted = await self.converter.convert(ctx, argument)
        else:
            mapping = {
                SlashCommandOptionType.string: str,
                SlashCommandOptionType.integer: int,
                SlashCommandOptionType.boolean: bool,
                SlashCommandOptionType.user: UserConverter,
                SlashCommandOptionType.channel: GuildChannelConverter,
                SlashCommandOptionType.role: RoleConverter,
                SlashCommandOptionType.mentionable: MentionableConverter,
                SlashCommandOptionType.number: float,
                SlashCommandOptionType.attachment: attachment_callback,
            }
            converter = mapping[self.input_type]
            if issubclass(converter, Converter):
                converted = await converter().convert(ctx, argument)
            else:
                converted = converter(argument)
        if self.choices:
            choices_names = [choice.name for choice in self.choices]
            if converted in choices_names:
                converted = get(self.choices, name=converted).value
            else:
                choices = [choice.value for choice in self.choices]
                if converted not in choices:
                    print(self.choices)
                    raise ValueError(
                        f"{argument} is not a valid choice. Valid choices: {list(set(choices_names + choices))}"
                    )

        return converted


discord.commands.options.Option = BridgeOption
