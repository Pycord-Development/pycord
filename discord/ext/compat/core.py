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
from typing import Union

import discord.commands.options
from discord.enums import SlashCommandOptionType
from discord.commands import SlashCommand, Option
from ..commands import Bot as ExtBot, AutoShardedBot as ExtAutoShardedBot, Command, Converter, UserConverter, \
    GuildChannelConverter, RoleConverter, BadArgument

__all__ = ("CompatCommand", "compat_command", "CompatExtCommand", "CompatSlashCommand")


class CompatSlashCommand(SlashCommand):
    ...


class CompatExtCommand(Command):
    ...


class CompatCommand:
    def __init__(self, callback, **kwargs):
        """
        This is the base class for commands that are compatible with both traditional (prefix-based) commands and slash
        commands.

        Parameters
        ----------
        callback: Callable[[CompatContext, ...], Awaitable[Any]]
            The callback to invoke when the command is executed. The first argument will be a :class:`CompatContext`,
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
        :class:`CompatExtCommand`
            The respective traditional (prefix-based) version of the command.
        """
        command = CompatExtCommand(self.callback, **self.kwargs)
        return command

    def get_application_command(self):
        """A method to get the discord.commands version of this command.

        Returns
        -------
        :class:`CompatSlashCommand`
            The respective slash command version of the command.
        """
        command = CompatSlashCommand(self.callback, **self.kwargs)
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


def compat_command(**kwargs):
    """A decorator that is used to wrap a function as a command.

    Parameters
    ----------
    kwargs: Optional[Dict[str, Any]]
        Keyword arguments that are directly passed to the respective command constructors.
    """
    def decorator(callback):
        return CompatCommand(callback, **kwargs)

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


class CompatOption(Option, Converter):
    async def convert(self, ctx, argument):
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
        if self.choices and converted not in self.choices:
            raise ValueError(f"{argument} is not a valid choice.")

        return converted


discord.commands.options.Option = CompatOption
