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

from __future__ import annotations  # will probably need in future for type hinting

from typing import Callable, Optional

import sys

from .client import Client
from .shard import AutoShardedClient
from .utils import get
from .app import (
    SlashCommand,
    SubCommandGroup,
    MessageCommand,
    UserCommand,
    ApplicationCommand,
    InteractionContext,
)
from .errors import Forbidden
from .interactions import Interaction


def command(cls=SlashCommand, **attrs):
    """A decorator that transforms a function into an :class:`.ApplicationCommand`. More specifically,
    usually one of :class:`.SlashCommand`, :class:`.UserCommand`, or :class:`.MessageCommand`. The exact class
    depends on the ``cls`` parameter.

    By default the ``description`` attribute is received automatically from the
    docstring of the function and is cleaned up with the use of
    ``inspect.cleandoc``. If the docstring is ``bytes``, then it is decoded
    into :class:`str` using utf-8 encoding.

    The ``name`` attribute also defaults to the function name unchanged.

    .. versionadded:: 2.0

    Parameters
    -----------
    cls: :class:`.ApplicationCommand`
        The class to construct with. By default this is :class:`.SlashCommand`.
        You usually do not change this.
    attrs
        Keyword arguments to pass into the construction of the class denoted
        by ``cls``.

    Raises
    -------
    TypeError
        If the function is not a coroutine or is already a command.
    """

    def decorator(func: Callable) -> cls:
        if isinstance(func, ApplicationCommand):
            func = func.callback
        elif not callable(func):
            raise TypeError(
                "func needs to be a callable or a subclass of ApplicationCommand."
            )

        return cls(func, **attrs)

    return decorator


class ApplicationCommandMixin:
    """A mixin that implements common functionality for classes that need
    application command compatibility.

    Attributes
    -----------
    app_commands: :class:`dict`
        A mapping of command id string to :class:`.ApplicationCommand` objects.
    to_register: :class:`list`
        A list of commands that have been added but not yet registered.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.to_register = []
        self.app_commands = {}

    def add_application_command(self, command: ApplicationCommand) -> None:
        """Adds a :class:`.ApplicationCommand` into the internal list of commands.

        This is usually not called, instead the :meth:`~.ApplicationMixin.command` or
        other shortcut decorators are used instead.

        .. versionadded:: 2.0

        Parameters
        -----------
        command: :class:`.ApplicationCommand`
            The command to add.
        """
        self.to_register.append(command)

    def remove_application_command(self, command: ApplicationCommand) -> Optional[ApplicationCommand]:
        """Remove a :class:`.ApplicationCommand` from the internal list
        of commands.

        .. versionadded:: 2.0

        Parameters
        -----------
        command: :class:`.ApplicationCommand`
            The command to remove.

        Returns
        --------
        Optional[:class:`.ApplicationCommand`]
            The command that was removed. If the name is not valid then
            ``None`` is returned instead.
        """
        return self.app_commands.pop(command.id)

    async def sync_commands(self) -> None:
        """|coro|

        Registers all commands that have been added through :meth:`.add_application_command`
        since :meth:`.register_commands`. This does not remove any registered commands that are not in the internal
        cache, like :meth:`.register_commands` does, but rather just adds new ones.

        This should usually be used instead of :meth:`.register_commands` when commands are already registered and you
        want to add more.

        This can cause bugs if you run this command excessively without using register_commands, as the bot's internal
        cache can get un-synced with discord's registered commands.

        .. versionadded:: 2.0
        """
        # TODO: Write this function as described in the docstring (bob will do this)
        return

    async def register_commands(self) -> None:
        """|coro|

        Registers all commands that have been added through :meth:`.add_application_command`.
        This method cleans up all commands over the API and should sync them with the internal cache of commands.

        By default, this coroutine is called inside the :func:`.on_connect`
        event. If you choose to override the :func:`.on_connect` event, then
        you should invoke this coroutine as well.

        .. versionadded:: 2.0
        """
        commands = []

        registered_commands = await self.http.get_global_commands(self.user.id)
        for command in [cmd for cmd in self.to_register if cmd.guild_ids is None]:
            as_dict = command.to_dict()
            if len(registered_commands) > 0:
                matches = [
                    x
                    for x in registered_commands
                    if x["name"] == command.name and x["type"] == command.type
                ]
                # TODO: rewrite this, it seems inefficient
                if matches:
                    as_dict["id"] = matches[0]["id"]
            commands.append(as_dict)

        update_guild_commands = {}
        async for guild in self.fetch_guilds(limit=None):
            update_guild_commands[guild.id] = []
        for command in [cmd for cmd in self.to_register if cmd.guild_ids is not None]:
            as_dict = command.to_dict()
            for guild_id in command.guild_ids:
                to_update = update_guild_commands[guild_id]
                update_guild_commands[guild_id] = to_update + [as_dict]

        for guild_id in update_guild_commands:
            try:
                cmds = await self.http.bulk_upsert_guild_commands(self.user.id, guild_id,
                                                                  update_guild_commands[guild_id])
            except Forbidden:
                if not update_guild_commands[guild_id]:
                    continue
                else:
                    print(f"Failed to add command to guild {guild_id}", file=sys.stderr)
                    raise
            else:
                for i in cmds:
                    cmd = get(self.to_register, name=i["name"], description=i["description"], type=i['type'])
                    self.app_commands[i["id"]] = cmd

        cmds = await self.http.bulk_upsert_global_commands(self.user.id, commands)

        for i in cmds:
            cmd = get(
                self.to_register,
                name=i["name"],
                description=i["description"],
                type=i["type"],
            )
            self.app_commands[i["id"]] = cmd

    async def handle_interaction(self, interaction: Interaction) -> None:
        """|coro|

        This function processes the commands that have been registered
        to the bot and other groups. Without this coroutine, none of the
        commands will be triggered.

        By default, this coroutine is called inside the :func:`.on_interaction`
        event. If you choose to override the :func:`.on_interaction` event, then
        you should invoke this coroutine as well.

        This function finds a registered command matching the interaction id from
        :attr:`.ApplicationCommandMixin.app_commands` and runs :meth:`ApplicationCommand.invoke` on it. If no matching
        command was found, it replies to the interaction with a default message.

        .. versionadded:: 2.0

        Parameters
        -----------
        interaction: :class:`discord.Interaction`
            The interaction to process
        """
        try:
            command = self.app_commands[interaction.data["id"]]
        except KeyError:
            self.dispatch("unknown_command", interaction)
        else:
            context = await self.get_application_context(interaction)
            await command.invoke(context)

    def slash_command(self, **kwargs):
        """A shortcut decorator that invokes :func:`.ApplicationCommandMixin.command` and adds it to
        the internal command list via :meth:`~.ApplicationCommandMixin.add_application_command`.
        This shortcut is made specifically for :class:`.SlashCommand`.

        .. versionadded:: 2.0

        Returns
        --------
        Callable[..., :class:`SlashCommand`]
            A decorator that converts the provided method into a :class:`.SlashCommand`, adds it to the bot,
            then returns it.
        """
        return self.application_command(cls=SlashCommand, **kwargs)

    def user_command(self, **kwargs):
        """A shortcut decorator that invokes :func:`.ApplicationCommandMixin.command` and adds it to
        the internal command list via :meth:`~.ApplicationCommandMixin.add_application_command`.
        This shortcut is made specifically for :class:`.UserCommand`.

        .. versionadded:: 2.0

        Returns
        --------
        Callable[..., :class:`UserCommand`]
            A decorator that converts the provided method into a :class:`.UserCommand`, adds it to the bot,
            then returns it.
        """
        return self.application_command(cls=UserCommand, **kwargs)

    def message_command(self, **kwargs):
        """A shortcut decorator that invokes :func:`.ApplicationCommandMixin.command` and adds it to
        the internal command list via :meth:`~.ApplicationCommandMixin.add_application_command`.
        This shortcut is made specifically for :class:`.MessageCommand`.

        .. versionadded:: 2.0

        Returns
        --------
        Callable[..., :class:`MessageCommand`]
            A decorator that converts the provided method into a :class:`.MessageCommand`, adds it to the bot,
            then returns it.
        """
        return self.application_command(cls=MessageCommand, **kwargs)

    def application_command(self, **kwargs):
        """A shortcut decorator that invokes :func:`.command` and adds it to
        the internal command list via :meth:`~.ApplicationCommandMixin.add_application_command`.

        .. versionadded:: 2.0

        Returns
        --------
        Callable[..., :class:`ApplicationCommand`]
            A decorator that converts the provided method into an :class:`.ApplicationCommand`, adds it to the bot,
            then returns it.
        """

        def decorator(func) -> ApplicationCommand:
            kwargs.setdefault("parent", self)
            result = command(**kwargs)(func)
            self.add_application_command(result)
            return result

        return decorator

    def command(self, **kwargs):
        """There is an alias for :meth:`application_command`.

        .. note::

            This decorator is overriden by :class:`commands.Bot`.

        .. versionadded:: 2.0

        Returns
        --------
        Callable[..., :class:`ApplicationCommand`]
            A decorator that converts the provided method into an :class:`.ApplicationCommand`, adds it to the bot,
            then returns it.
        """
        return self.application_command(**kwargs)

    def command_group(self, name: str, description: str, guild_ids=None) -> SubCommandGroup:
        # TODO: Write documentation for this. I'm not familiar enough with what this function does to do it myself.
        group = SubCommandGroup(name, description, guild_ids)
        self.add_application_command(group)
        return group

    async def get_application_context(
        self, interaction: Interaction, cls=None
    ) -> InteractionContext:
        r"""|coro|

        Returns the invocation context from the interaction.

        This is a more low-level counter-part for :meth:`.handle_interaction`
        to allow users more fine grained control over the processing.

        Parameters
        -----------
        interaction: :class:`discord.Interaction`
            The interaction to get the invocation context from.

        Returns
        --------
        :class:`.InteractionContext`
            The invocation context.
        """
        if cls == None:
            cls = InteractionContext
        return cls(self, interaction)


class BotBase(ApplicationCommandMixin):  # To Insert: CogMixin
    # TODO I think
    # def __init__(self, *args, **kwargs):
    #     super(Client, self).__init__(*args, **kwargs)

    async def on_connect(self):
        await self.register_commands()

    async def on_interaction(self, interaction):
        await self.handle_interaction(interaction)


class Bot(BotBase, Client):
    """Represents a discord bot.

    This class is a subclass of :class:`discord.Client` and as a result
    anything that you can do with a :class:`discord.Client` you can do with
    this bot.

    This class also subclasses :class:`.ApplicationCommandMixin` to provide the functionality
    to manage commands.

    .. versionadded:: 2.0
    """

    pass


class AutoShardedBot(BotBase, AutoShardedClient):
    """This is similar to :class:`.Bot` except that it is inherited from
    :class:`discord.AutoShardedClient` instead.

    .. versionadded:: 2.0
    """

    pass
