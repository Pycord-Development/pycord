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
import traceback
from .app.errors import CheckFailure  

from typing import Optional

import sys

from .client import Client
from .shard import AutoShardedClient
from .utils import get, async_all
from .app import (
    SlashCommand,
    SlashCommandGroup,
    MessageCommand,
    UserCommand,
    ApplicationCommand,
    ApplicationContext,
    command,
)

from .errors import Forbidden, DiscordException
from .interactions import Interaction


class ApplicationCommandMixin:
    """A mixin that implements common functionality for classes that need
    application command compatibility.

    Attributes
    -----------
    application_commands: :class:`dict`
        A mapping of command id string to :class:`.ApplicationCommand` objects.
    pending_application_commands: :class:`list`
        A list of commands that have been added but not yet registered. This is read-only and is modified via other
        methods.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._pending_application_commands = []
        self.application_commands = {}

    @property
    def pending_application_commands(self):
        return self._pending_application_commands

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
        debug_guild = getattr(self, 'debug_guilds', None)
        if debug_guild and command.guild_ids is None:
            command.guild_ids = self.debug_guilds
        self._pending_application_commands.append(command)

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
        return self.application_commands.pop(command.id)

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
        raise NotImplementedError

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
        for command in [cmd for cmd in self.pending_application_commands if cmd.guild_ids is None]:
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
        for command in [cmd for cmd in self.pending_application_commands if cmd.guild_ids is not None]:
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
                    cmd = get(self.pending_application_commands, name=i["name"], description=i["description"], type=i['type'])
                    self.application_commands[i["id"]] = cmd

        cmds = await self.http.bulk_upsert_global_commands(self.user.id, commands)

        for i in cmds:
            cmd = get(
                self.pending_application_commands,
                name=i["name"],
                description=i["description"],
                type=i["type"],
            )
            self.application_commands[i["id"]] = cmd

    async def process_application_commands(self, interaction: Interaction) -> None:
        """|coro|

        This function processes the commands that have been registered
        to the bot and other groups. Without this coroutine, none of the
        commands will be triggered.

        By default, this coroutine is called inside the :func:`.on_interaction`
        event. If you choose to override the :func:`.on_interaction` event, then
        you should invoke this coroutine as well.

        This function finds a registered command matching the interaction id from
        :attr:`.ApplicationCommandMixin.application_commands` and runs :meth:`ApplicationCommand.invoke` on it. If no matching
        command was found, it replies to the interaction with a default message.

        .. versionadded:: 2.0

        Parameters
        -----------
        interaction: :class:`discord.Interaction`
            The interaction to process
        """
        if not interaction.is_command():
            return

        try:
            command = self.application_commands[interaction.data["id"]]
        except KeyError:
            self.dispatch("unknown_command", interaction)
        else:
            ctx = await self.get_application_context(interaction)
            ctx.command = command
            self.dispatch('application_command', ctx)
            try:
                if await self.can_run(ctx, call_once=True):
                    await ctx.command.invoke(ctx)
                else:
                    raise CheckFailure('The global check once functions failed.')
            except DiscordException as exc:
                await ctx.command.dispatch_error(ctx, exc)
            else:
                self.dispatch('application_command_completion', ctx)

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

    def command_group(self, name: str, description: str, guild_ids=None) -> SlashCommandGroup:
        # TODO: Write documentation for this. I'm not familiar enough with what this function does to do it myself.
        group = SlashCommandGroup(name, description, guild_ids)
        self.add_application_command(group)
        return group

    async def get_application_context(
        self, interaction: Interaction, cls=None
    ) -> ApplicationContext:
        r"""|coro|

        Returns the invocation context from the interaction.

        This is a more low-level counter-part for :meth:`.process_application_commands`
        to allow users more fine grained control over the processing.

        Parameters
        -----------
        interaction: :class:`discord.Interaction`
            The interaction to get the invocation context from.
        cls
            The factory class that will be used to create the context.
            By default, this is :class:`.ApplicationContext`. Should a custom
            class be provided, it must be similar enough to
            :class:`.ApplicationContext`\'s interface.

        Returns
        --------
        :class:`.ApplicationContext`
            The invocation context. Tye type of this can change via the
            ``cls`` parameter.
        """
        if cls is None:
            cls = ApplicationContext
        return cls(self, interaction)


class BotBase(ApplicationCommandMixin):
    # TODO I think
    def __init__(self, *args, **kwargs):
        # super(Client, self).__init__(*args, **kwargs)
        # I replaced ^ with v and it worked
        super().__init__(*args, **kwargs)
        self.debug_guild = kwargs.pop("debug_guild", None)
        self.debug_guilds = kwargs.pop("debug_guilds", None)

        if self.debug_guild:
            if self.debug_guilds is None:
                self.debug_guilds = [self.debug_guild]
            else:
                raise TypeError('Both debug_guild and debug_guilds are set.')

        self._checks = []
        self._check_once = []
        self._before_invoke = None
        self._after_invoke = None

    async def on_connect(self):
        await self.register_commands()

    async def on_interaction(self, interaction):
        await self.process_application_commands(interaction)

    async def on_application_command_error(self, context: ApplicationContext, exception: DiscordException) -> None:
        """|coro|

        The default command error handler provided by the bot.

        By default this prints to :data:`sys.stderr` however it could be
        overridden to have a different implementation.

        This only fires if you do not specify any listeners for command error.
        """
        # TODO
        # if self.extra_events.get('on_application_command_error', None):
        #     return

        command = context.command
        if command and command.has_error_handler():
            return

        # TODO
        # cog = context.cog
        # if cog and cog.has_error_handler():
        #     return

        print(f'Ignoring exception in command {context.command}:', file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

    # global check registration
    # TODO: Remove these from commands.Bot

    def check(self, func):
        r"""A decorator that adds a global check to the bot.
        A global check is similar to a :func:`.check` that is applied
        on a per command basis except it is run before any command checks
        have been verified and applies to every command the bot has.
        .. note::
            This function can either be a regular function or a coroutine.
        Similar to a command :func:`.check`\, this takes a single parameter
        of type :class:`.Context` and can only raise exceptions inherited from
        :exc:`.CommandError`.
        Example
        ---------
        .. code-block:: python3
            @bot.check
            def check_commands(ctx):
                return ctx.command.qualified_name in allowed_commands
        """
        # T was used instead of Check to ensure the type matches on return
        self.add_check(func)  # type: ignore
        return func

    def add_check(self, func, *, call_once: bool = False) -> None:
        """Adds a global check to the bot.
        This is the non-decorator interface to :meth:`.check`
        and :meth:`.check_once`.
        Parameters
        -----------
        func
            The function that was used as a global check.
        call_once: :class:`bool`
            If the function should only be called once per
            :meth:`.invoke` call.
        """

        if call_once:
            self._check_once.append(func)
        else:
            self._checks.append(func)

    def remove_check(self, func, *, call_once: bool = False) -> None:
        """Removes a global check from the bot.
        This function is idempotent and will not raise an exception
        if the function is not in the global checks.
        Parameters
        -----------
        func
            The function to remove from the global checks.
        call_once: :class:`bool`
            If the function was added with ``call_once=True`` in
            the :meth:`.Bot.add_check` call or using :meth:`.check_once`.
        """
        l = self._check_once if call_once else self._checks

        try:
            l.remove(func)
        except ValueError:
            pass

    def check_once(self, func):
        r"""A decorator that adds a "call once" global check to the bot.
        Unlike regular global checks, this one is called only once
        per :meth:`.invoke` call.
        Regular global checks are called whenever a command is called
        or :meth:`.Command.can_run` is called. This type of check
        bypasses that and ensures that it's called only once, even inside
        the default help command.
        .. note::
            When using this function the :class:`.Context` sent to a group subcommand
            may only parse the parent command and not the subcommands due to it
            being invoked once per :meth:`.Bot.invoke` call.
        .. note::
            This function can either be a regular function or a coroutine.
        Similar to a command :func:`.check`\, this takes a single parameter
        of type :class:`.Context` and can only raise exceptions inherited from
        :exc:`.CommandError`.
        Example
        ---------
        .. code-block:: python3
            @bot.check_once
            def whitelist(ctx):
                return ctx.message.author.id in my_whitelist
        """
        self.add_check(func, call_once=True)
        return func

    async def can_run(self, ctx: ApplicationContext, *, call_once: bool = False) -> bool:
        data = self._check_once if call_once else self._checks

        if len(data) == 0:
            return True

        # type-checker doesn't distinguish between functions and methods
        return await async_all(f(ctx) for f in data)  # type: ignore


    def before_invoke(self, coro):
        """A decorator that registers a coroutine as a pre-invoke hook.
        A pre-invoke hook is called directly before the command is
        called. This makes it a useful function to set up database
        connections or any type of set up required.
        This pre-invoke hook takes a sole parameter, a :class:`.Context`.
        .. note::
            The :meth:`~.Bot.before_invoke` and :meth:`~.Bot.after_invoke` hooks are
            only called if all checks and argument parsing procedures pass
            without error. If any check or argument parsing procedures fail
            then the hooks are not called.
        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the pre-invoke hook.
        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The pre-invoke hook must be a coroutine.')

        self._before_invoke = coro
        return coro

    def after_invoke(self, coro):
        r"""A decorator that registers a coroutine as a post-invoke hook.
        A post-invoke hook is called directly after the command is
        called. This makes it a useful function to clean-up database
        connections or any type of clean up required.
        This post-invoke hook takes a sole parameter, a :class:`.Context`.
        .. note::
            Similar to :meth:`~.Bot.before_invoke`\, this is not called unless
            checks and argument parsing procedures succeed. This hook is,
            however, **always** called regardless of the internal command
            callback raising an error (i.e. :exc:`.CommandInvokeError`\).
            This makes it ideal for clean-up scenarios.
        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the post-invoke hook.
        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The post-invoke hook must be a coroutine.')

        self._after_invoke = coro
        return coro

class Bot(BotBase, Client):
    """Represents a discord bot.

    This class is a subclass of :class:`discord.Client` and as a result
    anything that you can do with a :class:`discord.Client` you can do with
    this bot.

    This class also subclasses :class:`.ApplicationCommandMixin` to provide the functionality
    to manage commands.

    .. versionadded:: 2.0

    Attributes
    -----------
    debug_guild: Optional[:class:`int`]
        Guild ID of a guild to use for testing commands. Prevents setting global commands
        in favor of guild commands, which update instantly.
        .. note::
            The bot will not create any global commands if a debug_guild is passed.
    debug_guilds: Optional[List[:class:`int`]]
        Guild IDs of guilds to use for testing commands. This is similar to debug_guild.
        .. note::
            You cannot set both debug_guild and debug_guilds.
    """

    pass


class AutoShardedBot(BotBase, AutoShardedClient):
    """This is similar to :class:`.Bot` except that it is inherited from
    :class:`discord.AutoShardedClient` instead.

    .. versionadded:: 2.0
    """

    pass