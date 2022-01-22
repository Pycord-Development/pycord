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

import asyncio
import collections
import inspect
import traceback
from .commands.errors import CheckFailure

from typing import (
    Any,
    Callable,
    Coroutine,
    Generator,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

import sys

from .client import Client
from .shard import AutoShardedClient
from .utils import MISSING, get, find, async_all
from .commands import (
    SlashCommand,
    SlashCommandGroup,
    MessageCommand,
    UserCommand,
    ApplicationCommand,
    ApplicationContext,
    AutocompleteContext,
    command,
)
from .cog import CogMixin

from .errors import Forbidden, DiscordException
from .interactions import Interaction
from .enums import InteractionType
from .user import User

CoroFunc = Callable[..., Coroutine[Any, Any, Any]]
CFT = TypeVar('CFT', bound=CoroFunc)

__all__ = (
    'ApplicationCommandMixin',
    'Bot',
    'AutoShardedBot',
)

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
        self._application_commands = {}

    @property
    def pending_application_commands(self):
        return self._pending_application_commands

    @property
    def commands(self) -> List[Union[ApplicationCommand, Any]]:
        commands = self.application_commands
        if self._supports_prefixed_commands:
            commands += self.prefixed_commands
        return commands

    @property
    def application_commands(self) -> List[ApplicationCommand]:
        return list(self._application_commands.values())

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
        if isinstance(command, SlashCommand) and command.is_subcommand:
            raise TypeError("The provided command is a sub-command of group")

        if self.debug_guilds and command.guild_ids is None:
            command.guild_ids = self.debug_guilds

        for cmd in self.pending_application_commands:
            if cmd == command:
                command.id = cmd.id
                self._application_commands[command.id] = command
                break
        self._pending_application_commands.append(command)

    def remove_application_command(
        self, command: ApplicationCommand
    ) -> Optional[ApplicationCommand]:
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
        return self._application_commands.pop(command.id)

    @property
    def get_command(self):
        """Shortcut for :meth:`.get_application_command`.
        
        .. note::
            Overridden in :class:`ext.commands.Bot`.
        
        .. versionadded:: 2.0
        """
        # TODO: Do something like we did in self.commands for this
        return self.get_application_command

    def get_application_command(
        self,
        name: str,
        guild_ids: Optional[List[int]] = None,
        type: Type[ApplicationCommand] = SlashCommand,
    ) -> Optional[ApplicationCommand]:
        """Get a :class:`.ApplicationCommand` from the internal list
        of commands.

        .. versionadded:: 2.0

        Parameters
        -----------
        name: :class:`str`
            The name of the command to get.
        guild_ids: List[:class:`int`]
            The guild ids associated to the command to get.
        type: Type[:class:`.ApplicationCommand`]
            The type of the command to get. Defaults to :class:`.SlashCommand`.

        Returns
        --------
        Optional[:class:`.ApplicationCommand`]
            The command that was requested. If not found, returns ``None``.
        """

        for command in self._application_commands.values():
            if (
                command.name == name
                and isinstance(command, type)
            ):
                if guild_ids is not None and command.guild_ids != guild_ids:
                    return
                return command

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
        This will only be rolled out to Discord if :meth:`.http.get_global_commands` has certain keys that differ from :data:`.pending_application_commands`
        By default, this coroutine is called inside the :func:`.on_connect`
        event. If you choose to override the :func:`.on_connect` event, then
        you should invoke this coroutine as well.
        .. versionadded:: 2.0
        """
        commands_to_bulk = []

        needs_bulk = False

        # Global Command Permissions
        global_permissions: List = []

        registered_commands = await self.http.get_global_commands(self.user.id)
        # 'Your app cannot have two global commands with the same name. Your app cannot have two guild commands within the same name on the same guild.'
        # We can therefore safely use the name of the command in our global slash commands as a unique identifier
        registered_commands_dict = {cmd["name"]:cmd for cmd in registered_commands}
        global_pending_application_commands_dict = {}
        
        for command in [
            cmd for cmd in self.pending_application_commands if cmd.guild_ids is None
        ]:
            as_dict = command.to_dict()
            
            global_pending_application_commands_dict[command.name] = as_dict
            if command.name in registered_commands_dict:
                match = registered_commands_dict[command.name]
            else:
                match = None
            # TODO: There is probably a far more efficient way of doing this
            # We want to check if the registered global command on Discord servers matches the given global commands
            if match:
                as_dict["id"] = match["id"]

                keys_to_check = {"default_permission": True, "name": True, "description": True, "options": ["type", "name", "description", "autocomplete", "choices"]}
                for key, more_keys in {
                    key:more_keys
                    for key, more_keys in keys_to_check.items()
                    if key in as_dict.keys()
                    if key in match.keys()
                }.items():
                    if key == "options":
                        for i, option_dict in enumerate(as_dict[key]):
                            if command.name == "recent":
                                print(option_dict, "|||||", match[key][i])
                            for key2 in more_keys:
                                pendingVal = None
                                if key2 in option_dict.keys():
                                    pendingVal = option_dict[key2]
                                    if pendingVal == False or pendingVal == []: # Registered commands are not available if choices is an empty array or if autocomplete is false
                                        pendingVal = None
                                matchVal = None
                                if key2 in match[key][i].keys():
                                    matchVal = match[key][i][key2]
                                    if matchVal == False or matchVal == []: # Registered commands are not available if choices is an empty array or if autocomplete is false
                                        matchVal = None

                                if pendingVal != matchVal:
                                    # When a property in the options of a pending global command is changed
                                    needs_bulk = True
                    else:
                        if as_dict[key] != match[key]:
                            # When a property in a pending global command is changed
                            needs_bulk = True
            else:
                # When a name of a pending global command is not registered in Discord
                needs_bulk = True

            commands_to_bulk.append(as_dict)
        
        for name, command in registered_commands_dict.items():
            if not name in global_pending_application_commands_dict.keys():
                # When a registered global command is not available in the pending global commands
                needs_bulk = True
    
        if needs_bulk:
            commands = await self.http.bulk_upsert_global_commands(self.user.id, commands_to_bulk)
        else:
            commands = registered_commands

        for i in commands:
            cmd = get(
                self.pending_application_commands,
                name=i["name"],
                guild_ids=None,
                type=i["type"],
            )
            if cmd:
                cmd.id = i["id"]
                self._application_commands[cmd.id] = cmd

                # Permissions (Roles will be converted to IDs just before Upsert for Global Commands)
                global_permissions.append({"id": i["id"], "permissions": cmd.permissions})

        update_guild_commands = {}
        async for guild in self.fetch_guilds(limit=None):
            update_guild_commands[guild.id] = []
        for command in [
            cmd
            for cmd in self.pending_application_commands
            if cmd.guild_ids is not None
        ]:
            as_dict = command.to_dict()
            for guild_id in command.guild_ids:
                to_update = update_guild_commands[guild_id]
                update_guild_commands[guild_id] = to_update + [as_dict]

        for guild_id, guild_data in update_guild_commands.items():
            try:
                commands = await self.http.bulk_upsert_guild_commands(
                    self.user.id, guild_id, update_guild_commands[guild_id]
                )

                # Permissions for this Guild
                guild_permissions: List = []
            except Forbidden:
                if not guild_data:
                    continue
                print(f"Failed to add command to guild {guild_id}", file=sys.stderr)
                raise
            else:
                for i in commands:
                    cmd = find(lambda cmd: cmd.name == i["name"] and cmd.type == i["type"] and int(i["guild_id"]) in cmd.guild_ids, self.pending_application_commands)
                    cmd.id = i["id"]
                    self._application_commands[cmd.id] = cmd

                    # Permissions
                    permissions = [
                        perm.to_dict()
                        for perm in cmd.permissions
                        if perm.guild_id is None
                        or (
                            perm.guild_id == guild_id and perm.guild_id in cmd.guild_ids
                        )
                    ]
                    guild_permissions.append(
                        {"id": i["id"], "permissions": permissions}
                    )

                for global_command in global_permissions:
                    permissions = [
                        perm.to_dict()
                        for perm in global_command["permissions"]
                        if perm.guild_id is None
                        or (
                            perm.guild_id == guild_id and perm.guild_id in cmd.guild_ids
                        )
                    ]
                    guild_permissions.append(
                        {"id": global_command["id"], "permissions": permissions}
                    )

                # Collect & Upsert Permissions for Each Guild
                # Command Permissions for this Guild
                guild_cmd_perms: List = []

                # Loop through Commands Permissions available for this Guild
                for item in guild_permissions:
                    new_cmd_perm = {"id": item["id"], "permissions": []}

                    # Replace Role / Owner Names with IDs
                    for permission in item["permissions"]:
                        if isinstance(permission["id"], str):
                            # Replace Role Names
                            if permission["type"] == 1:
                                role = get(
                                    self.get_guild(guild_id).roles,
                                    name=permission["id"],
                                )

                                # If not missing
                                if role is not None:
                                    new_cmd_perm["permissions"].append(
                                        {
                                            "id": role.id,
                                            "type": 1,
                                            "permission": permission["permission"],
                                        }
                                    )
                                else:
                                    print(
                                        "No Role ID found in Guild ({guild_id}) for Role ({role})".format(
                                            guild_id=guild_id, role=permission["id"]
                                        )
                                    )
                            # Add owner IDs
                            elif (
                                permission["type"] == 2 and permission["id"] == "owner"
                            ):
                                app = await self.application_info()  # type: ignore
                                if app.team:
                                    for m in app.team.members:
                                        new_cmd_perm["permissions"].append(
                                            {
                                                "id": m.id,
                                                "type": 2,
                                                "permission": permission["permission"],
                                            }
                                        )
                                else:
                                    new_cmd_perm["permissions"].append(
                                        {
                                            "id": app.owner.id,
                                            "type": 2,
                                            "permission": permission["permission"],
                                        }
                                    )
                        # Add the rest
                        else:
                            new_cmd_perm["permissions"].append(permission)

                    # Make sure we don't have over 10 overwrites
                    if len(new_cmd_perm["permissions"]) > 10:
                        print(
                            "Command '{name}' has more than 10 permission overrides in guild ({guild_id}).\nwill only use the first 10 permission overrides.".format(
                                name=self._application_commands[new_cmd_perm["id"]].name,
                                guild_id=guild_id,
                            )
                        )
                        new_cmd_perm["permissions"] = new_cmd_perm["permissions"][:10]

                    # Append to guild_cmd_perms
                    guild_cmd_perms.append(new_cmd_perm)

                # Upsert
                try:
                    await self.http.bulk_upsert_command_permissions(
                        self.user.id, guild_id, guild_cmd_perms
                    )
                except Forbidden:
                    print(
                        f"Failed to add command permissions to guild {guild_id}",
                        file=sys.stderr,
                    )
                    raise

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
        if interaction.type not in (
            InteractionType.application_command, 
            InteractionType.auto_complete
        ):
            return

        try:
            command = self._application_commands[interaction.data["id"]]
        except KeyError:
            for cmd in self.application_commands:
                if (
                    cmd.name == interaction.data["name"]
                    and interaction.data.get("guild_id", None) in cmd.guild_ids
                ):
                    command = cmd
                    break
            else:
                return self.dispatch("unknown_command", interaction)
        if interaction.type is InteractionType.auto_complete:
            ctx = await self.get_autocomplete_context(interaction)
            ctx.command = command
            return await command.invoke_autocomplete_callback(ctx)
        
        ctx = await self.get_application_context(interaction)
        ctx.command = command
        self.dispatch("application_command", ctx)
        try:
            if await self.can_run(ctx, call_once=True):
                await ctx.command.invoke(ctx)
            else:
                raise CheckFailure("The global check once functions failed.")
        except DiscordException as exc:
            await ctx.command.dispatch_error(ctx, exc)
        else:
            self.dispatch("application_command_completion", ctx)

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
            result = command(**kwargs)(func)
            self.add_application_command(result)
            return result

        return decorator

    def command(self, **kwargs):
        """There is an alias for :meth:`application_command`.

        .. note::

            This decorator is overridden by :class:`discord.ext.commands.Bot`.

        .. versionadded:: 2.0

        Returns
        --------
        Callable[..., :class:`ApplicationCommand`]
            A decorator that converts the provided method into an :class:`.ApplicationCommand`, adds it to the bot,
            then returns it.
        """
        return self.application_command(**kwargs)

    def create_group(
        self,
        name: str,
        description: Optional[str] = None,
        guild_ids: Optional[List[int]] = None,
    ) -> SlashCommandGroup:
        """A shortcut method that creates a slash command group with no subcommands and adds it to the internal
        command list via :meth:`~.ApplicationCommandMixin.add_application_command`.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: :class:`str`
            The name of the group to create.
        description: Optional[:class:`str`]
            The description of the group to create.
        guild_ids: Optional[List[:class:`int`]]
            A list of the IDs of each guild this group should be added to, making it a guild command.
            This will be a global command if ``None`` is passed.

        Returns
        --------
        SlashCommandGroup
            The slash command group that was created.
        """
        description = description or "No description provided."
        group = SlashCommandGroup(name, description, guild_ids)
        self.add_application_command(group)
        return group

    def group(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        guild_ids: Optional[List[int]] = None,
    ) -> Callable[[Type[SlashCommandGroup]], SlashCommandGroup]:
        """A shortcut decorator that initializes the provided subclass of :class:`.SlashCommandGroup`
        and adds it to the internal command list via :meth:`~.ApplicationCommandMixin.add_application_command`.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: Optional[:class:`str`]
            The name of the group to create. This will resolve to the name of the decorated class if ``None`` is passed.
        description: Optional[:class:`str`]
            The description of the group to create.
        guild_ids: Optional[List[:class:`int`]]
            A list of the IDs of each guild this group should be added to, making it a guild command.
            This will be a global command if ``None`` is passed.

        Returns
        --------
        Callable[[Type[SlashCommandGroup]], SlashCommandGroup]
            The slash command group that was created.
        """
        def inner(cls: Type[SlashCommandGroup]) -> SlashCommandGroup:
            group = cls(
                name or cls.__name__,
                (
                    description or inspect.cleandoc(cls.__doc__).splitlines()[0]
                    if cls.__doc__ is not None else "No description provided"
                ),
                guild_ids=guild_ids
            )
            self.add_application_command(group)
            return group
        return inner

    slash_group = group

    def walk_application_commands(self) -> Generator[ApplicationCommand, None, None]:
        """An iterator that recursively walks through all application commands and subcommands.

        Yields
        ------
        :class:`.ApplicationCommand`
            An application command from the internal list of application commands.
        """
        for command in self.application_commands:
            if isinstance(command, SlashCommandGroup):
                yield from command.walk_commands()
            yield command

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
            The invocation context. The type of this can change via the
            ``cls`` parameter.
        """
        if cls is None:
            cls = ApplicationContext
        return cls(self, interaction)

    async def get_autocomplete_context(
        self, interaction: Interaction, cls=None
    ) -> AutocompleteContext:
        r"""|coro|

        Returns the autocomplete context from the interaction.

        This is a more low-level counter-part for :meth:`.process_application_commands`
        to allow users more fine grained control over the processing.

        Parameters
        -----------
        interaction: :class:`discord.Interaction`
            The interaction to get the invocation context from.
        cls
            The factory class that will be used to create the context.
            By default, this is :class:`.AutocompleteContext`. Should a custom
            class be provided, it must be similar enough to
            :class:`.AutocompleteContext`\'s interface.

        Returns
        --------
        :class:`.AutocompleteContext`
            The autocomplete context. The type of this can change via the
            ``cls`` parameter.
        """
        if cls is None:
            cls = AutocompleteContext
        return cls(self, interaction)



class BotBase(ApplicationCommandMixin, CogMixin):
    _supports_prefixed_commands = False
    # TODO I think
    def __init__(self, description=None, *args, **options):
        # super(Client, self).__init__(*args, **kwargs)
        # I replaced ^ with v and it worked
        super().__init__(*args, **options)
        self.extra_events = {}  # TYPE: Dict[str, List[CoroFunc]]
        self.__cogs = {}  # TYPE: Dict[str, Cog]
        self.__extensions = {}  # TYPE: Dict[str, types.ModuleType]
        self._checks = []  # TYPE: List[Check]
        self._check_once = []
        self._before_invoke = None
        self._after_invoke = None
        self.description = inspect.cleandoc(description) if description else ""
        self.owner_id = options.get("owner_id")
        self.owner_ids = options.get("owner_ids", set())

        self.debug_guilds = options.pop("debug_guilds", None)

        if self.owner_id and self.owner_ids:
            raise TypeError("Both owner_id and owner_ids are set.")

        if self.owner_ids and not isinstance(
            self.owner_ids, collections.abc.Collection
        ):
            raise TypeError(
                f"owner_ids must be a collection not {self.owner_ids.__class__!r}"
            )

        self._checks = []
        self._check_once = []
        self._before_invoke = None
        self._after_invoke = None

    async def on_connect(self):
        await self.register_commands()

    async def on_interaction(self, interaction):
        await self.process_application_commands(interaction)

    async def on_application_command_error(
        self, context: ApplicationContext, exception: DiscordException
    ) -> None:
        """|coro|

        The default command error handler provided by the bot.

        By default this prints to :data:`sys.stderr` however it could be
        overridden to have a different implementation.

        This only fires if you do not specify any listeners for command error.
        """
        if self.extra_events.get('on_application_command_error', None):
            return

        command = context.command
        if command and command.has_error_handler():
            return

        cog = context.cog
        if cog and cog.has_error_handler():
            return

        print(f"Ignoring exception in command {context.command}:", file=sys.stderr)
        traceback.print_exception(
            type(exception), exception, exception.__traceback__, file=sys.stderr
        )

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

    async def can_run(
        self, ctx: ApplicationContext, *, call_once: bool = False
    ) -> bool:
        data = self._check_once if call_once else self._checks

        if len(data) == 0:
            return True

        # type-checker doesn't distinguish between functions and methods
        return await async_all(f(ctx) for f in data)  # type: ignore

    # listener registration

    def add_listener(self, func: CoroFunc, name: str = MISSING) -> None:
        """The non decorator alternative to :meth:`.listen`.

        Parameters
        -----------
        func: :ref:`coroutine <coroutine>`
            The function to call.
        name: :class:`str`
            The name of the event to listen for. Defaults to ``func.__name__``.

        Example
        --------

        .. code-block:: python3

            async def on_ready(): pass
            async def my_message(message): pass

            bot.add_listener(on_ready)
            bot.add_listener(my_message, 'on_message')
        """
        name = func.__name__ if name is MISSING else name

        if not asyncio.iscoroutinefunction(func):
            raise TypeError('Listeners must be coroutines')

        if name in self.extra_events:
            self.extra_events[name].append(func)
        else:
            self.extra_events[name] = [func]

    def remove_listener(self, func: CoroFunc, name: str = MISSING) -> None:
        """Removes a listener from the pool of listeners.

        Parameters
        -----------
        func
            The function that was used as a listener to remove.
        name: :class:`str`
            The name of the event we want to remove. Defaults to
            ``func.__name__``.
        """

        name = func.__name__ if name is MISSING else name

        if name in self.extra_events:
            try:
                self.extra_events[name].remove(func)
            except ValueError:
                pass

    def listen(self, name: str = MISSING) -> Callable[[CFT], CFT]:
        """A decorator that registers another function as an external
        event listener. Basically this allows you to listen to multiple
        events from different places e.g. such as :func:`.on_ready`

        The functions being listened to must be a :ref:`coroutine <coroutine>`.

        Example
        --------

        .. code-block:: python3

            @bot.listen()
            async def on_message(message):
                print('one')

            # in some other file...

            @bot.listen('on_message')
            async def my_message(message):
                print('two')

        Would print one and two in an unspecified order.

        Raises
        -------
        TypeError
            The function being listened to is not a coroutine.
        """

        def decorator(func: CFT) -> CFT:
            self.add_listener(func, name)
            return func

        return decorator

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        # super() will resolve to Client
        super().dispatch(event_name, *args, **kwargs)  # type: ignore
        ev = 'on_' + event_name
        for event in self.extra_events.get(ev, []):
            self._schedule_event(event, ev, *args, **kwargs)  # type: ignore

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
            raise TypeError("The pre-invoke hook must be a coroutine.")

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
            raise TypeError("The post-invoke hook must be a coroutine.")

        self._after_invoke = coro
        return coro

    async def is_owner(self, user: User) -> bool:
        """|coro|

        Checks if a :class:`~discord.User` or :class:`~discord.Member` is the owner of
        this bot.

        If an :attr:`owner_id` is not set, it is fetched automatically
        through the use of :meth:`~.Bot.application_info`.

        .. versionchanged:: 1.3
            The function also checks if the application is team-owned if
            :attr:`owner_ids` is not set.

        Parameters
        -----------
        user: :class:`.abc.User`
            The user to check for.

        Returns
        --------
        :class:`bool`
            Whether the user is the owner.
        """

        if self.owner_id:
            return user.id == self.owner_id
        elif self.owner_ids:
            return user.id in self.owner_ids
        else:
            app = await self.application_info()  # type: ignore
            if app.team:
                self.owner_ids = ids = {m.id for m in app.team.members}
                return user.id in ids
            else:
                self.owner_id = owner_id = app.owner.id
                return user.id == owner_id


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
    description: :class:`str`
        The content prefixed into the default help message.
    owner_id: Optional[:class:`int`]
        The user ID that owns the bot. If this is not set and is then queried via
        :meth:`.is_owner` then it is fetched automatically using
        :meth:`~.Bot.application_info`.
    owner_ids: Optional[Collection[:class:`int`]]
        The user IDs that owns the bot. This is similar to :attr:`owner_id`.
        If this is not set and the application is team based, then it is
        fetched automatically using :meth:`~.Bot.application_info`.
        For performance reasons it is recommended to use a :class:`set`
        for the collection. You cannot set both ``owner_id`` and ``owner_ids``.

        .. versionadded:: 1.3
           
    debug_guilds: Optional[List[:class:`int`]]
        Guild IDs of guilds to use for testing commands. This is similar to debug_guild.
        The bot will not create any global commands if a debug_guilds is passed.
    """

    pass


class AutoShardedBot(BotBase, AutoShardedClient):
    """This is similar to :class:`.Bot` except that it is inherited from
    :class:`discord.AutoShardedClient` instead.

    .. versionadded:: 2.0
    """

    pass
