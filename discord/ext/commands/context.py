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
from __future__ import annotations

import inspect
import re
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union

import discord.abc
import discord.utils
from discord.message import Message

from ...commands import ApplicationContext, BaseContext

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    from .bot import AutoShardedBot, Bot
    from .cog import Cog
    from .core import Command
    from .help import HelpCommand
    from .view import StringView

__all__ = ("Context",)

MISSING: Any = discord.utils.MISSING


T = TypeVar("T")
BotT = TypeVar("BotT", bound="Union[Bot, AutoShardedBot]")
CogT = TypeVar("CogT", bound="Cog")

if TYPE_CHECKING:
    P = ParamSpec("P")
else:
    P = TypeVar("P")


class Context(BaseContext, Generic[BotT]):
    """Represents the context in which a command is being invoked under.

    This class contains a lot of metadata to help you understand more about
    the invocation context. This class is not created manually and is instead
    passed around to commands as the first parameter.

    This class implements the :class:`~discord.abc.Messageable` ABC.

    Attributes
    ----------
    message: :class:`.Message`
        The message that triggered the command being executed.
    current_parameter: Optional[:class:`inspect.Parameter`]
        The parameter that is currently being inspected and converted.
        This is only of use for within converters.

        .. versionadded:: 2.0
    prefix: Optional[:class:`str`]
        The prefix that was used to invoke the command.
    command_failed: :class:`bool`
        A boolean that indicates if the command failed to be parsed, checked,
        or invoked.
    """

    command: Command | None

    def __init__(
        self,
        *,
        message: Message,
        bot: BotT,
        view: StringView,
        args: list[Any] = MISSING,
        kwargs: dict[str, Any] = MISSING,
        prefix: str | None = None,
        command: Command | None = None,
        current_parameter: inspect.Parameter | None = None,
        **kwargs2: dict[str, Any],
    ):
        super().__init__(bot=bot, command=command, args=args, kwargs=kwargs, **kwargs2)

        self.message: Message = message
        self.prefix: str | None = prefix
        self.view: StringView = view
        self.current_parameter: inspect.Parameter | None = current_parameter

    @property
    def source(self) -> Message:
        return self.message

    @discord.utils.copy_doc(ApplicationContext.reinvoke)
    async def reinvoke(self, *, call_hooks: bool = False, restart: bool = True) -> None:
        cmd = self.command
        view = self.view
        if cmd is None:
            raise ValueError("This context is not valid.")

        # some state to revert to when we're done
        index, previous = view.index, view.previous
        invoked_with = self.invoked_with
        invoked_subcommand = self.invoked_subcommand
        invoked_parents = self.invoked_parents
        subcommand_passed = self.subcommand_passed

        if restart:
            to_call = cmd.root_parent or cmd
            view.index = len(self.prefix or "")
            view.previous = 0
            self.invoked_parents = []
            self.invoked_with = view.get_word()  # advance to get the root command
        else:
            to_call = cmd

        try:
            await to_call.reinvoke(self, call_hooks=call_hooks)
        finally:
            self.command = cmd
            view.index = index
            view.previous = previous
            self.invoked_with = invoked_with
            self.invoked_subcommand = invoked_subcommand
            self.invoked_parents = invoked_parents
            self.subcommand_passed = subcommand_passed

    @property
    def valid(self) -> bool:
        """Checks if the invocation context is valid to be invoked with."""
        return self.prefix is not None and self.command is not None

    @property
    def clean_prefix(self) -> str:
        """The cleaned up invoke prefix. i.e. mentions are ``@name`` instead of ``<@id>``.

        .. versionadded:: 2.0
        """
        if self.prefix is None:
            return ""

        user = self.me
        # this breaks if the prefix mention is not the bot itself, but I
        # consider this to be an *incredibly* strange use case. I'd rather go
        # for this common use case rather than waste performance for the
        # odd one.
        pattern = re.compile(r"<@!?%s>" % user.id)
        return pattern.sub("@%s" % user.display_name.replace("\\", r"\\"), self.prefix)

    async def send_help(self, *args: Any) -> Any:
        """send_help(entity=<bot>)

        |coro|

        Shows the help command for the specified entity if given.
        The entity can be a command or a cog.

        If no entity is given, then it'll show help for the
        entire bot.

        If the entity is a string, then it looks up whether it's a
        :class:`Cog` or a :class:`Command`.

        .. note::

            Due to the way this function works, instead of returning
            something similar to :meth:`~.commands.HelpCommand.command_not_found`
            this returns :class:`None` on bad input or no help command.

        Parameters
        ----------
        entity: Optional[Union[:class:`Command`, :class:`Cog`, :class:`str`]]
            The entity to show help for.

        Returns
        -------
        Any
            The result of the help command, if any.
        """
        from ...commands.mixins import wrap_callback
        from .core import Group
        from .errors import CommandError

        bot = self.bot
        cmd = bot.help_command

        if cmd is None:
            return None

        cmd = cmd.copy()
        cmd.context = self
        if len(args) == 0:
            await cmd.prepare_help_command(self, None)
            mapping = cmd.get_bot_mapping()
            injected = wrap_callback(cmd.send_bot_help)
            try:
                return await injected(mapping)
            except CommandError as e:
                await cmd.on_help_command_error(self, e)
                return None

        entity = args[0]
        if isinstance(entity, str):
            entity = bot.get_cog(entity) or bot.get_command(entity)

        if entity is None:
            return None

        try:
            entity.qualified_name
        except AttributeError:
            # if we're here then it's not a cog, group, or command.
            return None

        await cmd.prepare_help_command(self, entity.qualified_name)

        try:
            if hasattr(entity, "__cog_commands__"):
                injected = wrap_callback(cmd.send_cog_help)
                return await injected(entity)
            elif isinstance(entity, Group):
                injected = wrap_callback(cmd.send_group_help)
                return await injected(entity)
            elif isinstance(entity, Command):
                injected = wrap_callback(cmd.send_command_help)
                return await injected(entity)
            else:
                return None
        except CommandError as e:
            await cmd.on_help_command_error(self, e)

    @discord.utils.copy_doc(Message.reply)
    async def reply(self, content: str | None = None, **kwargs: Any) -> Message:
        return await self.message.reply(content, **kwargs)
