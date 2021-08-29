import copy
import logging
import re
import typing
from contextlib import suppress
from inspect import getdoc, iscoroutinefunction

import discord
from discord.ext import commands

from . import context, error, http, model
from .utils import manage_commands
from .utils.manage_components import get_components_ids, get_messages_ids


def _get_val(d: dict, key):  # util function to get value from dict with fallback to None key
    try:
        value = d[key]
    except KeyError:  # if there is no specific key set, we fallback to "global/any"
        value = d[None]
    return value


class SlashCommand:
    """
    Slash command handler class.

    :param client: discord.py Client or Bot instance.
    :type client: Union[discord.Client, discord.ext.commands.Bot]
    :param sync_commands: Whether to sync commands automatically. Default `False`.
    :type sync_commands: bool
    :param debug_guild: Guild ID of guild to use for testing commands. Prevents setting global commands in favor of guild commands, which update instantly
    :type debug_guild: int
    :param delete_from_unused_guilds: If the bot should make a request to set no commands for guilds that haven't got any commands registered in :class:``SlashCommand``. Default `False`.
    :type delete_from_unused_guilds: bool
    :param sync_on_cog_reload: Whether to sync commands on cog reload. Default `False`.
    :type sync_on_cog_reload: bool
    :param override_type: Whether to override checking type of the client and try register event.
    :type override_type: bool
    :param application_id: The application id of the bot, required only when the application id and bot id are different. (old bots)
    :type application_id: int

    .. note::
        If ``sync_on_cog_reload`` is enabled, command syncing will be triggered when :meth:`discord.ext.commands.Bot.reload_extension`
        is triggered.

    :ivar _discord: Discord client of this client.
    :ivar commands: Dictionary of the registered commands via :func:`.slash` decorator.
    :ivar menu_commands: Dictionary of the registered context menus via the :func:`.context_menu` decorator.
    :ivar req: :class:`.http.SlashCommandRequest` of this client.
    :ivar logger: Logger of this client.
    :ivar sync_commands: Whether to sync commands automatically.
    :ivar sync_on_cog_reload: Whether to sync commands on cog reload.
    :ivar has_listener: Whether discord client has listener add function.
    """

    def __init__(
        self,
        client: typing.Union[discord.Client, commands.Bot],
        sync_commands: bool = False,
        debug_guild: typing.Optional[int] = None,
        delete_from_unused_guilds: bool = False,
        sync_on_cog_reload: bool = False,
        override_type: bool = False,
        application_id: typing.Optional[int] = None,
    ):
        self._discord = client
        self.commands = {"context": {}}
        self.subcommands = {}
        self.components = {}
        self.logger = logging.getLogger("discord_slash")
        self.req = http.SlashCommandRequest(self.logger, self._discord, application_id)
        self.sync_commands = sync_commands
        self.debug_guild = debug_guild
        self.sync_on_cog_reload = sync_on_cog_reload

        if self.sync_commands:
            self._discord.loop.create_task(self.sync_all_commands(delete_from_unused_guilds))

        if (
            not isinstance(client, commands.Bot)
            and not isinstance(client, commands.AutoShardedBot)
            and not override_type
        ):
            self.logger.warning(
                "Detected discord.Client! It is highly recommended to use `commands.Bot`. Do not add any `on_socket_response` event."
            )

            self._discord.on_socket_response = self.on_socket_response
            self.has_listener = False
        else:
            if not hasattr(self._discord, "slash"):
                self._discord.slash = self
            else:
                raise error.DuplicateSlashClient("You can't have duplicate SlashCommand instances!")

            self._discord.add_listener(self.on_socket_response)
            self.has_listener = True
            default_add_function = self._discord.add_cog

            def override_add_cog(cog: commands.Cog):
                default_add_function(cog)
                self.get_cog_commands(cog)

            self._discord.add_cog = override_add_cog
            default_remove_function = self._discord.remove_cog

            def override_remove_cog(name: str):
                cog = self._discord.get_cog(name)
                if cog is None:
                    return
                self.remove_cog_commands(cog)
                default_remove_function(name)

            self._discord.remove_cog = override_remove_cog

            if self.sync_on_cog_reload:
                orig_reload = self._discord.reload_extension

                def override_reload_extension(*args):
                    orig_reload(*args)
                    self._discord.loop.create_task(
                        self.sync_all_commands(delete_from_unused_guilds)
                    )

                self._discord.reload_extension = override_reload_extension

    def get_cog_commands(self, cog: commands.Cog):
        """
        Gets slash command from :class:`discord.ext.commands.Cog`.

        .. note::
            Since version ``1.0.9``, this gets called automatically during cog initialization.

        :param cog: Cog that has slash commands.
        :type cog: discord.ext.commands.Cog
        """
        if hasattr(cog, "_slash_registered"):  # Temporary warning
            return self.logger.warning(
                "Calling get_cog_commands is no longer required "
                "to add cog slash commands. Make sure to remove all calls to this function."
            )
        cog._slash_registered = True  # Assuming all went well
        func_list = [getattr(cog, x) for x in dir(cog)]

        self._get_cog_slash_commands(cog, func_list)
        self._get_cog_component_callbacks(cog, func_list)

    def _get_cog_slash_commands(self, cog, func_list):
        res = [
            x
            for x in func_list
            if isinstance(x, (model.CogBaseCommandObject, model.CogSubcommandObject))
        ]

        for x in res:
            x.cog = cog
            if isinstance(x, model.CogBaseCommandObject):
                if x.name in self.commands:
                    raise error.DuplicateCommand(x.name)
                self.commands[x.name] = x
            else:
                if x.base in self.commands:
                    base_command = self.commands[x.base]
                    for i in x.allowed_guild_ids:
                        if i not in base_command.allowed_guild_ids:
                            base_command.allowed_guild_ids.append(i)

                    base_permissions = x.base_command_data["api_permissions"]
                    if base_permissions:
                        for applicable_guild in base_permissions:
                            if applicable_guild not in base_command.permissions:
                                base_command.permissions[applicable_guild] = []
                            base_command.permissions[applicable_guild].extend(
                                base_permissions[applicable_guild]
                            )

                    self.commands[x.base].has_subcommands = True

                else:
                    self.commands[x.base] = model.BaseCommandObject(x.base, x.base_command_data)
                if x.base not in self.subcommands:
                    self.subcommands[x.base] = {}
                if x.subcommand_group:
                    if x.subcommand_group not in self.subcommands[x.base]:
                        self.subcommands[x.base][x.subcommand_group] = {}
                    if x.name in self.subcommands[x.base][x.subcommand_group]:
                        raise error.DuplicateCommand(f"{x.base} {x.subcommand_group} {x.name}")
                    self.subcommands[x.base][x.subcommand_group][x.name] = x
                else:
                    if x.name in self.subcommands[x.base]:
                        raise error.DuplicateCommand(f"{x.base} {x.name}")
                    self.subcommands[x.base][x.name] = x

    def _get_cog_component_callbacks(self, cog, func_list):
        res = [x for x in func_list if isinstance(x, model.CogComponentCallbackObject)]

        for x in res:
            x.cog = cog
            self._add_comp_callback_obj(x)

    def remove_cog_commands(self, cog):
        """
        Removes slash command from :class:`discord.ext.commands.Cog`.

        .. note::
            Since version ``1.0.9``, this gets called automatically during cog de-initialization.

        :param cog: Cog that has slash commands.
        :type cog: discord.ext.commands.Cog
        """
        if hasattr(cog, "_slash_registered"):
            del cog._slash_registered
        func_list = [getattr(cog, x) for x in dir(cog)]
        self._remove_cog_slash_commands(func_list)
        self._remove_cog_component_callbacks(func_list)

    def _remove_cog_slash_commands(self, func_list):
        res = [
            x
            for x in func_list
            if isinstance(x, (model.CogBaseCommandObject, model.CogSubcommandObject))
        ]
        for x in res:
            if isinstance(x, model.CogBaseCommandObject):
                if x.name not in self.commands:
                    continue  # Just in case it is removed due to subcommand.
                if x.name in self.subcommands:
                    self.commands[x.name].func = None
                    continue  # Let's remove completely when every subcommand is removed.
                del self.commands[x.name]
            else:
                if x.base not in self.subcommands:
                    continue  # Just in case...
                if x.subcommand_group:
                    del self.subcommands[x.base][x.subcommand_group][x.name]
                    if not self.subcommands[x.base][x.subcommand_group]:
                        del self.subcommands[x.base][x.subcommand_group]
                else:
                    del self.subcommands[x.base][x.name]
                if not self.subcommands[x.base]:
                    del self.subcommands[x.base]
                    if x.base in self.commands:
                        if self.commands[x.base].func:
                            self.commands[x.base].has_subcommands = False
                        else:
                            del self.commands[x.base]

    def _remove_cog_component_callbacks(self, func_list):
        res = [x for x in func_list if isinstance(x, model.CogComponentCallbackObject)]

        for x in res:
            self.remove_component_callback_obj(x)

    async def to_dict(self):
        """
        Converts all commands currently registered to :class:`SlashCommand` to a dictionary.
        Returns a dictionary in the format:

        .. code-block:: python

            {
                "global" : [], # list of global commands
                "guild" : {
                    0000: [] # list of commands in the guild 0000
                }
            }

        Commands are in the format specified by discord `here <https://discord.com/developers/docs/interactions/slash-commands#applicationcommand>`_
        """
        await self._discord.wait_until_ready()  # In case commands are still not registered to SlashCommand.
        all_guild_ids = []
        for x in self.commands:
            if x == "context":
                # handle context menu separately.
                for _x in self.commands["context"]:
                    _selected = self.commands["context"][_x]
                    for i in _selected.allowed_guild_ids:
                        if i not in all_guild_ids:
                            all_guild_ids.append(i)
                continue
            for i in self.commands[x].allowed_guild_ids:
                if i not in all_guild_ids:
                    all_guild_ids.append(i)
        cmds = {"global": [], "guild": {x: [] for x in all_guild_ids}}
        wait = {}  # Before merging to return dict, let's first put commands to temporary dict.
        for x in self.commands:
            if x == "context":
                # handle context menu separately.
                for _x in self.commands["context"]:  # x is the new reference dict
                    selected = self.commands["context"][_x]

                    if selected.allowed_guild_ids:
                        for y in selected.allowed_guild_ids:
                            if y not in wait:
                                wait[y] = {}
                            command_dict = {
                                "name": _x,
                                "options": selected.options or [],
                                "default_permission": selected.default_permission,
                                "permissions": {},
                                "type": selected._type,
                            }
                            if y in selected.permissions:
                                command_dict["permissions"][y] = selected.permissions[y]
                            wait[y][_x] = copy.deepcopy(command_dict)
                    else:
                        if "global" not in wait:
                            wait["global"] = {}
                        command_dict = {
                            "name": _x,
                            "options": selected.options or [],
                            "default_permission": selected.default_permission,
                            "permissions": selected.permissions or {},
                            "type": selected._type,
                        }
                        wait["global"][_x] = copy.deepcopy(command_dict)

                continue

            selected = self.commands[x]
            if selected.allowed_guild_ids:
                for y in selected.allowed_guild_ids:
                    if y not in wait:
                        wait[y] = {}
                    command_dict = {
                        "name": x,
                        "description": selected.description or "No Description.",
                        "options": selected.options or [],
                        "default_permission": selected.default_permission,
                        "permissions": {},
                        "type": selected._type,
                    }
                    if command_dict["type"] != 1:
                        command_dict.pop("description")
                    if y in selected.permissions:
                        command_dict["permissions"][y] = selected.permissions[y]
                    wait[y][x] = copy.deepcopy(command_dict)
            else:
                if "global" not in wait:
                    wait["global"] = {}
                command_dict = {
                    "name": x,
                    "description": selected.description or "No Description.",
                    "options": selected.options or [],
                    "default_permission": selected.default_permission,
                    "permissions": selected.permissions or {},
                    "type": selected._type,
                }
                if command_dict["type"] != 1:
                    command_dict.pop("description")
                wait["global"][x] = copy.deepcopy(command_dict)

        # Separated normal command add and subcommand add not to
        # merge subcommands to one. More info at Issue #88
        # https://github.com/eunwoo1104/discord-py-slash-command/issues/88

        for x in self.commands:
            if x == "context":
                continue  # no menus have subcommands.

            if not self.commands[x].has_subcommands:
                continue
            tgt = self.subcommands[x]
            for y in tgt:
                sub = tgt[y]
                if isinstance(sub, model.SubcommandObject):
                    _dict = {
                        "name": sub.name,
                        "description": sub.description or "No Description.",
                        "type": model.SlashCommandOptionType.SUB_COMMAND,
                        "options": sub.options or [],
                    }
                    if sub.allowed_guild_ids:
                        for z in sub.allowed_guild_ids:
                            wait[z][x]["options"].append(_dict)
                    else:
                        wait["global"][x]["options"].append(_dict)
                else:
                    queue = {}
                    base_dict = {
                        "name": y,
                        "description": "No Description.",
                        "type": model.SlashCommandOptionType.SUB_COMMAND_GROUP,
                        "options": [],
                    }
                    for z in sub:
                        sub_sub = sub[z]
                        _dict = {
                            "name": sub_sub.name,
                            "description": sub_sub.description or "No Description.",
                            "type": model.SlashCommandOptionType.SUB_COMMAND,
                            "options": sub_sub.options or [],
                        }
                        if sub_sub.allowed_guild_ids:
                            for i in sub_sub.allowed_guild_ids:
                                if i not in queue:
                                    queue[i] = copy.deepcopy(base_dict)
                                queue[i]["options"].append(_dict)
                        else:
                            if "global" not in queue:
                                queue["global"] = copy.deepcopy(base_dict)
                            queue["global"]["options"].append(_dict)
                    for i in queue:
                        wait[i][x]["options"].append(queue[i])

        for x in wait:
            if x == "global":
                [cmds["global"].append(n) for n in wait["global"].values()]
            else:
                [cmds["guild"][x].append(n) for n in wait[x].values()]

        return cmds

    async def sync_all_commands(
        self, delete_from_unused_guilds=False, delete_perms_from_unused_guilds=False
    ):
        """
        Matches commands registered on Discord to commands registered here.
        Deletes any commands on Discord but not here, and registers any not on Discord.
        This is done with a `put` request.
        A PUT request will only be made if there are changes detected.
        If ``sync_commands`` is ``True``, then this will be automatically called.

        :param delete_from_unused_guilds: If the bot should make a request to set no commands for guilds that haven't got any commands registered in :class:``SlashCommand``
        :param delete_perms_from_unused_guilds: If the bot should make a request to clear permissions for guilds that haven't got any permissions registered in :class:``SlashCommand``
        """
        permissions_map = {}
        cmds = await self.to_dict()
        self.logger.info("Syncing commands...")
        # if debug_guild is set, global commands get re-routed to the guild to update quickly
        cmds_formatted = {self.debug_guild: cmds["global"]}
        for guild in cmds["guild"]:
            cmds_formatted[guild] = cmds["guild"][guild]

        for scope in cmds_formatted:
            permissions = {}
            new_cmds = cmds_formatted[scope]
            existing_cmds = await self.req.get_all_commands(guild_id=scope)
            existing_by_name = {}
            to_send = []
            changed = False
            for cmd in existing_cmds:
                existing_by_name[cmd["name"]] = model.CommandData(**cmd)

            if len(new_cmds) != len(existing_cmds):
                changed = True

            for command in new_cmds:
                cmd_name = command["name"]
                permissions[cmd_name] = command.pop("permissions")
                if cmd_name in existing_by_name:
                    cmd_data = model.CommandData(**command)
                    existing_cmd = existing_by_name[cmd_name]
                    if cmd_data != existing_cmd:
                        changed = True
                        to_send.append(command)
                    else:
                        command_with_id = command
                        command_with_id["id"] = existing_cmd.id
                        to_send.append(command_with_id)
                else:
                    changed = True
                    to_send.append(command)

            if changed:
                self.logger.debug(
                    f"Detected changes on {scope if scope is not None else 'global'}, updating them"
                )
                try:
                    existing_cmds = await self.req.put_slash_commands(
                        slash_commands=to_send, guild_id=scope
                    )
                except discord.HTTPException as ex:
                    if ex.status == 400:
                        # catch bad requests
                        cmd_nums = set(
                            re.findall(r"^[\w-]{1,32}$", ex.args[0])
                        )  # find all discords references to commands
                        error_string = ex.args[0]

                        for num in cmd_nums:
                            error_command = to_send[int(num)]
                            error_string = error_string.replace(
                                f"In {num}",
                                f"'{error_command.get('name')}'",
                            )

                        ex.args = (error_string,)

                    raise ex
            else:
                self.logger.debug(
                    f"Detected no changes on {scope if scope is not None else 'global'}, skipping"
                )

            id_name_map = {}
            for cmd in existing_cmds:
                id_name_map[cmd["name"]] = cmd["id"]

            for cmd_name in permissions:
                cmd_permissions = permissions[cmd_name]
                cmd_id = id_name_map[cmd_name]
                for applicable_guild in cmd_permissions:
                    if applicable_guild not in permissions_map:
                        permissions_map[applicable_guild] = []
                    permission = {
                        "id": cmd_id,
                        "guild_id": applicable_guild,
                        "permissions": cmd_permissions[applicable_guild],
                    }
                    permissions_map[applicable_guild].append(permission)

        self.logger.info("Syncing permissions...")
        self.logger.debug(f"Commands permission data are {permissions_map}")
        for scope in permissions_map:
            existing_perms = await self.req.get_all_guild_commands_permissions(scope)
            new_perms = permissions_map[scope]

            changed = False
            if len(existing_perms) != len(new_perms):
                changed = True
            else:
                existing_perms_model = {}
                for existing_perm in existing_perms:
                    existing_perms_model[existing_perm["id"]] = model.GuildPermissionsData(
                        **existing_perm
                    )
                for new_perm in new_perms:
                    if new_perm["id"] not in existing_perms_model:
                        changed = True
                        break
                    if existing_perms_model[new_perm["id"]] != model.GuildPermissionsData(
                        **new_perm
                    ):
                        changed = True
                        break

            if changed:
                self.logger.debug(f"Detected permissions changes on {scope}, updating them")
                await self.req.update_guild_commands_permissions(scope, new_perms)
            else:
                self.logger.debug(f"Detected no permissions changes on {scope}, skipping")

        if delete_from_unused_guilds:
            self.logger.info("Deleting unused guild commands...")
            other_guilds = [
                guild.id for guild in self._discord.guilds if guild.id not in cmds["guild"]
            ]
            # This is an extremly bad way to do this, because slash cmds can be in guilds the bot isn't in
            # But it's the only way until discord makes an endpoint to request all the guild with cmds registered.

            for guild in other_guilds:
                with suppress(discord.Forbidden):
                    existing = await self.req.get_all_commands(guild_id=guild)
                    if len(existing) != 0:
                        self.logger.debug(f"Deleting commands from {guild}")
                        await self.req.put_slash_commands(slash_commands=[], guild_id=guild)

        if delete_perms_from_unused_guilds:
            self.logger.info("Deleting unused guild permissions...")
            other_guilds = [
                guild.id for guild in self._discord.guilds if guild.id not in permissions_map.keys()
            ]
            for guild in other_guilds:
                with suppress(discord.Forbidden):
                    self.logger.debug(f"Deleting permissions from {guild}")
                    existing_perms = await self.req.get_all_guild_commands_permissions(guild)
                    if len(existing_perms) != 0:
                        await self.req.update_guild_commands_permissions(guild, [])

        self.logger.info("Completed syncing all commands!")

    def add_slash_command(
        self,
        cmd,
        name: str = None,
        description: str = None,
        guild_ids: typing.List[int] = None,
        options: list = None,
        default_permission: bool = True,
        permissions: typing.Dict[int, list] = None,
        connector: dict = None,
        has_subcommands: bool = False,
    ):
        """
        Registers slash command to SlashCommand.

        .. warning::
            Just using this won't register slash command to Discord API.
            To register it, check :meth:`.utils.manage_commands.add_slash_command` or simply enable `sync_commands`.

        :param cmd: Command Coroutine.
        :type cmd: Coroutine
        :param name: Name of the slash command. Default name of the coroutine.
        :type name: str
        :param description: Description of the slash command. Defaults to command docstring or ``None``.
        :type description: str
        :param guild_ids: List of Guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        :param options: Options of the slash command. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
        :type options: list
        :param default_permission: Sets if users have permission to run slash command by default, when no permissions are set. Default ``True``.
        :type default_permission: bool
        :param permissions: Dictionary of permissions of the slash command. Key being target guild_id and value being a list of permissions to apply. Default ``None``.
        :type permissions: dict
        :param connector: Kwargs connector for the command. Default ``None``.
        :type connector: dict
        :param has_subcommands: Whether it has subcommand. Default ``False``.
        :type has_subcommands: bool
        """
        name = name or cmd.__name__
        name = name.lower()
        guild_ids = guild_ids if guild_ids else []
        if not all(isinstance(item, int) for item in guild_ids):
            raise error.IncorrectGuildIDType(
                f"The snowflake IDs {guild_ids} given are not a list of integers. Because of discord.py convention, please use integer IDs instead. Furthermore, the command '{name}' will be deactivated and broken until fixed."
            )
        if name in self.commands:
            tgt = self.commands[name]
            if not tgt.has_subcommands:
                raise error.DuplicateCommand(name)
            has_subcommands = tgt.has_subcommands
            for x in tgt.allowed_guild_ids:
                if x not in guild_ids:
                    guild_ids.append(x)

        description = description or getdoc(cmd)

        if options is None:
            options = manage_commands.generate_options(cmd, description, connector)

        _cmd = {
            "func": cmd,
            "description": description,
            "guild_ids": guild_ids,
            "api_options": options,
            "default_permission": default_permission,
            "api_permissions": permissions,
            "connector": connector or {},
            "has_subcommands": has_subcommands,
        }
        obj = model.BaseCommandObject(name, _cmd)
        self.commands[name] = obj
        self.logger.debug(f"Added command `{name}`")
        return obj

    def _cog_ext_add_context_menu(self, target: int, name: str, guild_ids: list = None):
        """
        Creates a new cog_based context menu command.

        :param cmd: Command Coroutine.
        :type cmd: Coroutine
        :param name: The name of the command
        :type name: str
        :param _type: The context menu type.
        :type _type: int
        """

    def add_context_menu(self, cmd, name: str, _type: int, guild_ids: list = None):
        """
        Creates a new context menu command.

        :param cmd: Command Coroutine.
        :type cmd: Coroutine
        :param name: The name of the command
        :type name: str
        :param _type: The context menu type.
        :type _type: int
        """

        name = [name or cmd.__name__][0]
        guild_ids = guild_ids or []

        if not all(isinstance(item, int) for item in guild_ids):
            raise error.IncorrectGuildIDType(
                f"The snowflake IDs {guild_ids} given are not a list of integers. Because of discord.py convention, please use integer IDs instead. Furthermore, the command '{name}' will be deactivated and broken until fixed."
            )

        if name in self.commands["context"]:
            tgt = self.commands["context"][name]
            if not tgt.has_subcommands:
                raise error.DuplicateCommand(name)
            has_subcommands = tgt.has_subcommands  # noqa
            for x in tgt.allowed_guild_ids:
                if x not in guild_ids:
                    guild_ids.append(x)

        _cmd = {
            "default_permission": None,
            "has_permissions": None,
            "name": name,
            "type": _type,
            "func": cmd,
            "description": "",
            "guild_ids": guild_ids,
            "api_options": [],
            "connector": {},
            "has_subcommands": False,
            "api_permissions": {},
        }

        obj = model.BaseCommandObject(name, cmd=_cmd, _type=_type)
        self.commands["context"][name] = obj
        self.logger.debug(f"Added context command `{name}`")
        return obj

    def add_subcommand(
        self,
        cmd,
        base,
        subcommand_group=None,
        name=None,
        description: str = None,
        base_description: str = None,
        base_default_permission: bool = True,
        base_permissions: typing.Dict[int, list] = None,
        subcommand_group_description: str = None,
        guild_ids: typing.List[int] = None,
        options: list = None,
        connector: dict = None,
    ):
        """
        Registers subcommand to SlashCommand.

        :param cmd: Subcommand Coroutine.
        :type cmd: Coroutine
        :param base: Name of the base command.
        :type base: str
        :param subcommand_group: Name of the subcommand group, if any. Default ``None`` which represents there is no sub group.
        :type subcommand_group: str
        :param name: Name of the subcommand. Default name of the coroutine.
        :type name: str
        :param description: Description of the subcommand. Defaults to command docstring or ``None``.
        :type description: str
        :param base_description: Description of the base command. Default ``None``.
        :type base_description: str
        :param base_default_permission: Sets if users have permission to run base command by default, when no permissions are set. Default ``True``.
        :type base_default_permission: bool
        :param base_permissions: Dictionary of permissions of the slash command. Key being target guild_id and value being a list of permissions to apply. Default ``None``.
        :type base_permissions: dict
        :param subcommand_group_description: Description of the subcommand_group. Default ``None``.
        :type subcommand_group_description: str
        :param guild_ids: List of guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        :param options: Options of the subcommand. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
        :type options: list
        :param connector: Kwargs connector for the command. Default ``None``.
        :type connector: dict
        """
        base = base.lower()
        subcommand_group = subcommand_group.lower() if subcommand_group else subcommand_group
        name = name or cmd.__name__
        name = name.lower()
        description = description or getdoc(cmd)
        guild_ids = guild_ids if guild_ids else []
        if not all(isinstance(item, int) for item in guild_ids):
            raise error.IncorrectGuildIDType(
                f"The snowflake IDs {guild_ids} given are not a list of integers. Because of discord.py convention, please use integer IDs instead. Furthermore, the command '{name}' will be deactivated and broken until fixed."
            )

        if base in self.commands:
            for x in guild_ids:
                if x not in self.commands[base].allowed_guild_ids:
                    self.commands[base].allowed_guild_ids.append(x)

        if options is None:
            options = manage_commands.generate_options(cmd, description, connector)

        _cmd = {
            "func": None,
            "description": base_description,
            "guild_ids": guild_ids.copy(),
            "api_options": [],
            "default_permission": base_default_permission,
            "api_permissions": base_permissions,
            "connector": {},
            "has_subcommands": True,
        }
        _sub = {
            "func": cmd,
            "name": name,
            "description": description,
            "base_desc": base_description,
            "sub_group_desc": subcommand_group_description,
            "guild_ids": guild_ids,
            "api_options": options,
            "connector": connector or {},
        }
        if base not in self.commands:
            self.commands[base] = model.BaseCommandObject(base, _cmd)
        else:
            base_command = self.commands[base]
            base_command.has_subcommands = True
            if base_permissions:
                for applicable_guild in base_permissions:
                    if applicable_guild not in base_command.permissions:
                        base_command.permissions[applicable_guild] = []
                    base_command.permissions[applicable_guild].extend(
                        base_permissions[applicable_guild]
                    )
            if base_command.description:
                _cmd["description"] = base_command.description
        if base not in self.subcommands:
            self.subcommands[base] = {}
        if subcommand_group:
            if subcommand_group not in self.subcommands[base]:
                self.subcommands[base][subcommand_group] = {}
            if name in self.subcommands[base][subcommand_group]:
                raise error.DuplicateCommand(f"{base} {subcommand_group} {name}")
            obj = model.SubcommandObject(_sub, base, name, subcommand_group)
            self.subcommands[base][subcommand_group][name] = obj
        else:
            if name in self.subcommands[base]:
                raise error.DuplicateCommand(f"{base} {name}")
            obj = model.SubcommandObject(_sub, base, name)
            self.subcommands[base][name] = obj
        self.logger.debug(
            f"Added subcommand `{base} {subcommand_group or ''} {name or cmd.__name__}`"
        )
        return obj

    def slash(
        self,
        *,
        name: str = None,
        description: str = None,
        guild_ids: typing.List[int] = None,
        options: typing.List[dict] = None,
        default_permission: bool = True,
        permissions: dict = None,
        connector: dict = None,
    ):
        """
        Decorator that registers coroutine as a slash command.\n
        All decorator args must be passed as keyword-only args.\n
        1 arg for command coroutine is required for ctx(:class:`.model.SlashContext`),
        and if your slash command has some args, then those args are also required.\n
        All args must be passed as keyword-args.

        .. note::
            If you don't pass `options` but has extra args, then it will automatically generate options.
            However, it is not recommended to use it since descriptions will be "No Description." or the command's description.

        .. warning::
            Unlike discord.py's command, ``*args``, keyword-only args, converters, etc. are not supported or behave differently.

        Example:

        .. code-block:: python

            @slash.slash(name="ping")
            async def _slash(ctx): # Normal usage.
                await ctx.send(content=f"Pong! (`{round(bot.latency*1000)}`ms)")


            @slash.slash(name="pick")
            async def _pick(ctx, choice1, choice2): # Command with 1 or more args.
                await ctx.send(content=str(random.choice([choice1, choice2])))

        To format the connector, follow this example.

        .. code-block:: python

            {
                "example-arg": "example_arg",
                "시간": "hour"
                # Formatting connector is required for
                # using other than english for option parameter name
                # for in case.
            }

        Set discord UI's parameter name as key, and set command coroutine's arg name as value.

        :param name: Name of the slash command. Default name of the coroutine.
        :type name: str
        :param description: Description of the slash command. Default ``None``.
        :type description: str
        :param guild_ids: List of Guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        :param options: Options of the slash command. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
        :type options: List[dict]
        :param default_permission: Sets if users have permission to run slash command by default, when no permissions are set. Default ``True``.
        :type default_permission: bool
        :param permissions: Permission requirements of the slash command. Default ``None``.
        :type permissions: dict
        :param connector: Kwargs connector for the command. Default ``None``.
        :type connector: dict
        """
        if not permissions:
            permissions = {}

        def wrapper(cmd):
            decorator_permissions = getattr(cmd, "__permissions__", None)
            if decorator_permissions:
                permissions.update(decorator_permissions)

            obj = self.add_slash_command(
                cmd,
                name,
                description,
                guild_ids,
                options,
                default_permission,
                permissions,
                connector,
            )

            return obj

        return wrapper

    def subcommand(
        self,
        *,
        base,
        subcommand_group=None,
        name=None,
        description: str = None,
        base_description: str = None,
        base_desc: str = None,
        base_default_permission: bool = True,
        base_permissions: dict = None,
        subcommand_group_description: str = None,
        sub_group_desc: str = None,
        guild_ids: typing.List[int] = None,
        options: typing.List[dict] = None,
        connector: dict = None,
    ):
        """
        Decorator that registers subcommand.\n
        Unlike discord.py, you don't need base command.\n
        All args must be passed as keyword-args.

        .. note::
            If you don't pass `options` but has extra args, then it will automatically generate options.
            However, it is not recommended to use it since descriptions will be "No Description." or the command's description.

        .. warning::
            Unlike discord.py's command, ``*args``, keyword-only args, converters, etc. are not supported or behave differently.

        Example:

        .. code-block:: python

            # /group say <str>
            @slash.subcommand(base="group", name="say")
            async def _group_say(ctx, _str):
                await ctx.send(content=_str)

            # /group kick user <user>
            @slash.subcommand(base="group",
                              subcommand_group="kick",
                              name="user")
            async def _group_kick_user(ctx, user):
                ...

        :param base: Name of the base command.
        :type base: str
        :param subcommand_group: Name of the subcommand group, if any. Default ``None`` which represents there is no sub group.
        :type subcommand_group: str
        :param name: Name of the subcommand. Default name of the coroutine.
        :type name: str
        :param description: Description of the subcommand. Default ``None``.
        :type description: str
        :param base_description: Description of the base command. Default ``None``.
        :type base_description: str
        :param base_desc: Alias of ``base_description``.
        :param base_default_permission: Sets if users have permission to run slash command by default, when no permissions are set. Default ``True``.
        :type base_default_permission: bool
        :param permissions: Permission requirements of the slash command. Default ``None``.
        :type permissions: dict
        :param subcommand_group_description: Description of the subcommand_group. Default ``None``.
        :type subcommand_group_description: str
        :param sub_group_desc: Alias of ``subcommand_group_description``.
        :param guild_ids: List of guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        :param options: Options of the subcommand. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
        :type options: List[dict]
        :param connector: Kwargs connector for the command. Default ``None``.
        :type connector: dict
        """
        base_description = base_description or base_desc
        subcommand_group_description = subcommand_group_description or sub_group_desc
        if not base_permissions:
            base_permissions = {}

        def wrapper(cmd):
            decorator_permissions = getattr(cmd, "__permissions__", None)
            if decorator_permissions:
                base_permissions.update(decorator_permissions)

            obj = self.add_subcommand(
                cmd,
                base,
                subcommand_group,
                name,
                description,
                base_description,
                base_default_permission,
                base_permissions,
                subcommand_group_description,
                guild_ids,
                options,
                connector,
            )

            return obj

        return wrapper

    def permission(self, guild_id: int, permissions: list):
        """
        Decorator that add permissions. This will set the permissions for a single guild, you can use it more than once for each command.

        :param guild_id: ID of the guild for the permissions.
        :type guild_id: int
        :param permissions: List of permissions to be set for the specified guild.
        :type permissions: list
        """

        def wrapper(cmd):
            if not getattr(cmd, "__permissions__", None):
                cmd.__permissions__ = {}
            cmd.__permissions__[guild_id] = permissions
            return cmd

        return wrapper

    def context_menu(self, *, target: int, name: str, guild_ids: list = None):
        """
        Decorator that adds context menu commands.

        :param target: The type of menu.
        :type target: int
        :param name: A name to register as the command in the menu.
        :type name: str
        :param guild_ids: A list of guild IDs to register the command under. Defaults to ``None``.
        :type guild_ids: list
        """

        def wrapper(cmd):
            # _obj = self.add_slash_command(
            #    cmd,
            #    name,
            #    "",
            #    guild_ids
            # )

            # This has to call both, as its a arg-less menu.

            obj = self.add_context_menu(cmd, name, target, guild_ids)

            return obj

        return wrapper

    def add_component_callback(
        self,
        callback: typing.Coroutine,
        *,
        messages: typing.Union[int, discord.Message, list] = None,
        components: typing.Union[str, dict, list] = None,
        use_callback_name=True,
        component_type: int = None,
    ):
        """
        Adds a coroutine callback to a component.
        Callback can be made to only accept component interactions from a specific messages
        and/or custom_ids of components.

        :param Coroutine callback: The coroutine to be called when the component is interacted with. Must accept a single argument with the type :class:`.context.ComponentContext`.
        :param messages: If specified, only interactions from the message given will be accepted. Can be a message object to check for, or the message ID or list of previous two. Empty list will mean that no interactions are accepted.
        :type messages: Union[discord.Message, int, list]
        :param components: If specified, only interactions with ``custom_id`` of given components will be accepted. Defaults to the name of ``callback`` if ``use_callback_name=True``. Can be a custom ID (str) or component dict (actionrow or button) or list of previous two.
        :type components: Union[str, dict, list]
        :param use_callback_name: Whether the ``custom_id`` defaults to the name of ``callback`` if unspecified. If ``False``, either ``messages`` or ``components`` must be specified.
        :type use_callback_name: bool
        :param component_type: The type of the component to avoid collisions with other component types. See :class:`.model.ComponentType`.
        :type component_type: Optional[int]
        :raises: .error.DuplicateCustomID, .error.IncorrectFormat
        """

        message_ids = list(get_messages_ids(messages)) if messages is not None else [None]
        custom_ids = list(get_components_ids(components)) if components is not None else [None]

        if use_callback_name and custom_ids == [None]:
            custom_ids = [callback.__name__]

        if message_ids == [None] and custom_ids == [None]:
            raise error.IncorrectFormat("You must specify messages or components (or both)")

        callback_obj = model.ComponentCallbackObject(
            callback, message_ids, custom_ids, component_type
        )
        self._add_comp_callback_obj(callback_obj)
        return callback_obj

    def _add_comp_callback_obj(self, callback_obj):
        component_type = callback_obj.component_type

        for message_id, custom_id in callback_obj.keys:
            self._register_comp_callback_obj(callback_obj, message_id, custom_id, component_type)

    def _register_comp_callback_obj(self, callback_obj, message_id, custom_id, component_type):
        message_id_dict = self.components
        custom_id_dict = message_id_dict.setdefault(message_id, {})
        component_type_dict = custom_id_dict.setdefault(custom_id, {})

        if component_type in component_type_dict:
            raise error.DuplicateCallback(message_id, custom_id, component_type)

        component_type_dict[component_type] = callback_obj
        self.logger.debug(
            f"Added component callback for "
            f"message ID {message_id or '<any>'}, "
            f"custom_id `{custom_id or '<any>'}`, "
            f"component_type `{component_type or '<any>'}`"
        )

    def extend_component_callback(
        self,
        callback_obj: model.ComponentCallbackObject,
        message_id: int = None,
        custom_id: str = None,
    ):
        """
        Registers existing callback object (:class:`.model.ComponentCallbackObject`)
        for specific combination of message_id, custom_id, component_type.

        :param callback_obj: callback object.
        :type callback_obj: model.ComponentCallbackObject
        :param message_id: If specified, only removes the callback for the specific message ID.
        :type message_id: Optional[.model]
        :param custom_id: The ``custom_id`` of the component.
        :type custom_id: Optional[str]
        :raises: .error.DuplicateCustomID, .error.IncorrectFormat
        """

        component_type = callback_obj.component_type
        self._register_comp_callback_obj(callback_obj, message_id, custom_id, component_type)
        callback_obj.keys.add((message_id, custom_id))

    def get_component_callback(
        self,
        message_id: int = None,
        custom_id: str = None,
        component_type: int = None,
    ):
        """
        Returns component callback (or None if not found) for specific combination of message_id, custom_id, component_type.

        :param message_id: If specified, only removes the callback for the specific message ID.
        :type message_id: Optional[.model]
        :param custom_id: The ``custom_id`` of the component.
        :type custom_id: Optional[str]
        :param component_type: The type of the component. See :class:`.model.ComponentType`.
        :type component_type: Optional[int]

        :return: Optional[model.ComponentCallbackObject]
        """
        message_id_dict = self.components
        try:
            custom_id_dict = _get_val(message_id_dict, message_id)
            component_type_dict = _get_val(custom_id_dict, custom_id)
            callback = _get_val(component_type_dict, component_type)

        except KeyError:  # there was no key in dict and no global fallback
            pass
        else:
            return callback

    def remove_component_callback(
        self, message_id: int = None, custom_id: str = None, component_type: int = None
    ):
        """
        Removes a component callback from specific combination of message_id, custom_id, component_type.

        :param message_id: If specified, only removes the callback for the specific message ID.
        :type message_id: Optional[int]
        :param custom_id: The ``custom_id`` of the component.
        :type custom_id: Optional[str]
        :param component_type: The type of the component. See :class:`.model.ComponentType`.
        :type component_type: Optional[int]
        :raises: .error.IncorrectFormat
        """
        try:
            callback = self.components[message_id][custom_id].pop(component_type)
            if not self.components[message_id][custom_id]:  # delete dict nesting levels if empty
                self.components[message_id].pop(custom_id)
                if not self.components[message_id]:
                    self.components.pop(message_id)
        except KeyError:
            raise error.IncorrectFormat(
                f"Callback for "
                f"message ID `{message_id or '<any>'}`, "
                f"custom_id `{custom_id or '<any>'}`, "
                f"component_type `{component_type or '<any>'}` is not registered!"
            )
        else:
            callback.keys.remove((message_id, custom_id))

    def remove_component_callback_obj(self, callback_obj: model.ComponentCallbackObject):
        """
        Removes a component callback from all related message_id, custom_id listeners.

        :param callback_obj: callback object.
        :type callback_obj: model.ComponentCallbackObject
        :raises: .error.IncorrectFormat
        """
        if not callback_obj.keys:
            raise error.IncorrectFormat("Callback already removed from any listeners")

        component_type = callback_obj.component_type
        for message_id, custom_id in callback_obj.keys.copy():
            self.remove_component_callback(message_id, custom_id, component_type)

    def component_callback(
        self,
        *,
        messages: typing.Union[int, discord.Message, list] = None,
        components: typing.Union[str, dict, list] = None,
        use_callback_name=True,
        component_type: int = None,
    ):
        """
        Decorator that registers a coroutine as a component callback.
        Adds a coroutine callback to a component.
        Callback can be made to only accept component interactions from a specific messages
        and/or custom_ids of components.

        :param messages: If specified, only interactions from the message given will be accepted. Can be a message object to check for, or the message ID or list of previous two. Empty list will mean that no interactions are accepted.
        :type messages: Union[discord.Message, int, list]
        :param components: If specified, only interactions with ``custom_id`` of given components will be accepted. Defaults to the name of ``callback`` if ``use_callback_name=True``. Can be a custom ID (str) or component dict (actionrow or button) or list of previous two.
        :type components: Union[str, dict, list]
        :param use_callback_name: Whether the ``custom_id`` defaults to the name of ``callback`` if unspecified. If ``False``, either ``messages`` or ``components`` must be specified.
        :type use_callback_name: bool
        :param component_type: The type of the component to avoid collisions with other component types. See :class:`.model.ComponentType`.
        :type component_type: Optional[int]
        :raises: .error.DuplicateCustomID, .error.IncorrectFormat
        """

        def wrapper(callback):
            return self.add_component_callback(
                callback,
                messages=messages,
                components=components,
                use_callback_name=use_callback_name,
                component_type=component_type,
            )

        return wrapper

    async def process_options(
        self,
        guild: discord.Guild,
        options: list,
        connector: dict,
        temporary_auto_convert: dict = None,
    ) -> dict:
        """
        Processes Role, User, and Channel option types to discord.py's models.

        :param guild: Guild of the command message.
        :type guild: discord.Guild
        :param options: Dict of options.
        :type options: list
        :param connector: Kwarg connector.
        :param temporary_auto_convert: Temporary parameter, use this if options doesn't have ``type`` keyword.
        :return: Union[list, dict]
        """

        if not guild or not isinstance(guild, discord.Guild):
            return {connector.get(x["name"]) or x["name"]: x["value"] for x in options}

        converters = [
            # If extra converters are added and some needs to fetch it,
            # you should pass as a list with 1st item as a cache get method
            # and 2nd as a actual fetching method.
            [guild.get_member, guild.fetch_member],
            guild.get_channel,
            guild.get_role,
        ]

        types = {
            "user": 0,
            "USER": 0,
            model.SlashCommandOptionType.USER: 0,
            "6": 0,
            6: 0,
            "channel": 1,
            "CHANNEL": 1,
            model.SlashCommandOptionType.CHANNEL: 1,
            "7": 1,
            7: 1,
            "role": 2,
            "ROLE": 2,
            model.SlashCommandOptionType.ROLE: 2,
            8: 2,
            "8": 2,
        }

        to_return = {}

        for x in options:
            processed = None  # This isn't the best way, but we should to reduce duplicate lines.

            # This is to temporarily fix Issue #97, that on Android device
            # does not give option type from API.
            if "type" not in x:
                x["type"] = temporary_auto_convert[x["name"]]

            if x["type"] not in types:
                processed = x["value"]
            else:
                loaded_converter = converters[types[x["type"]]]
                if isinstance(loaded_converter, list):  # For user type.
                    cache_first = loaded_converter[0](int(x["value"]))
                    if cache_first:
                        processed = cache_first
                    else:
                        loaded_converter = loaded_converter[1]
                if not processed:
                    try:
                        processed = (
                            await loaded_converter(int(x["value"]))
                            if iscoroutinefunction(loaded_converter)
                            else loaded_converter(int(x["value"]))
                        )
                    except (
                        discord.Forbidden,
                        discord.HTTPException,
                        discord.NotFound,
                    ):  # Just in case.
                        self.logger.warning("Failed fetching discord object! Passing ID instead.")
                        processed = int(x["value"])
            to_return[connector.get(x["name"]) or x["name"]] = processed
        return to_return

    async def invoke_command(self, func, ctx, args):
        """
        Invokes command.

        :param func: Command coroutine.
        :param ctx: Context.
        :param args: Args. Can be list or dict.
        """
        try:
            if isinstance(args, dict):
                ctx.kwargs = args
                ctx.args = list(args.values())
            await func.invoke(ctx, **args)
        except Exception as ex:
            if not await self._handle_invoke_error(func, ctx, ex):
                await self.on_slash_command_error(ctx, ex)

    async def invoke_component_callback(self, func, ctx):
        """
        Invokes component callback.

        :param func: Component callback object.
        :param ctx: Context.
        """
        try:
            await func.invoke(ctx)
        except Exception as ex:
            if not await self._handle_invoke_error(func, ctx, ex):
                await self.on_component_callback_error(ctx, ex)

    async def _handle_invoke_error(self, func, ctx, ex):
        if hasattr(func, "on_error"):
            if func.on_error is not None:
                try:
                    if hasattr(func, "cog"):
                        await func.on_error(func.cog, ctx, ex)
                    else:
                        await func.on_error(ctx, ex)
                    return True
                except Exception as e:
                    self.logger.error(f"{ctx.command}:: Error using error decorator: {e}")
        return False

    async def on_socket_response(self, msg):
        """
        This event listener is automatically registered at initialization of this class.

        .. warning::
            DO NOT MANUALLY REGISTER, OVERRIDE, OR WHATEVER ACTION TO THIS COROUTINE UNLESS YOU KNOW WHAT YOU ARE DOING.

        :param msg: Gateway message.
        """
        if msg["t"] != "INTERACTION_CREATE":
            return

        to_use = msg["d"]
        interaction_type = to_use["type"]

        # dis_snek variance seq

        if interaction_type in (1, 2):
            await self._on_slash(to_use)
            await self._on_context_menu(to_use)
        elif interaction_type == 3:
            try:
                await self._on_component(to_use)  # noqa
            except KeyError:
                pass  # for some reason it complains about custom_id being an optional arg when it's fine?
            finally:
                await self._on_context_menu(to_use)
        else:
            raise NotImplementedError(
                f"Unknown Interaction Received: {interaction_type}"
            )  # check if discord does a sneaky event change on us
        return

    async def _on_component(self, to_use):
        ctx = context.ComponentContext(self.req, to_use, self._discord, self.logger)
        self._discord.dispatch("component", ctx)

        callback = self.get_component_callback(
            ctx.origin_message_id, ctx.custom_id, ctx.component_type
        )
        if callback is not None:
            self._discord.dispatch("component_callback", ctx, callback)
            await self.invoke_component_callback(callback, ctx)

    async def _on_slash(self, to_use):  # slash commands only.
        if to_use["data"]["name"] in self.commands:

            ctx = context.SlashContext(self.req, to_use, self._discord, self.logger)
            cmd_name = to_use["data"]["name"]

            if cmd_name not in self.commands and cmd_name in self.subcommands:
                return await self.handle_subcommand(ctx, to_use)

            selected_cmd = self.commands[to_use["data"]["name"]]

            if type(selected_cmd) == dict:
                return  # this is context dict storage.

            if selected_cmd._type != 1:
                return  # If its a menu, ignore.

            if (
                selected_cmd.allowed_guild_ids
                and ctx.guild_id not in selected_cmd.allowed_guild_ids
            ):
                return

            if selected_cmd.has_subcommands and not selected_cmd.func:
                return await self.handle_subcommand(ctx, to_use)

            if "options" in to_use["data"]:
                for x in to_use["data"]["options"]:
                    if "value" not in x:
                        return await self.handle_subcommand(ctx, to_use)

            # This is to temporarily fix Issue #97, that on Android device
            # does not give option type from API.
            temporary_auto_convert = {}
            for x in selected_cmd.options:
                temporary_auto_convert[x["name"].lower()] = x["type"]

            args = (
                await self.process_options(
                    ctx.guild,
                    to_use["data"]["options"],
                    selected_cmd.connector,
                    temporary_auto_convert,
                )
                if "options" in to_use["data"]
                else {}
            )

            self._discord.dispatch("slash_command", ctx)

            await self.invoke_command(selected_cmd, ctx, args)

    async def _on_context_menu(self, to_use):
        # Slash Command Logic

        # to prevent any potential keyerrors:
        if "name" not in to_use["data"].keys():
            return

        if to_use["data"]["name"] in self.commands["context"]:
            ctx = context.MenuContext(self.req, to_use, self._discord, self.logger)
            cmd_name = to_use["data"]["name"]

            if cmd_name not in self.commands["context"] and cmd_name in self.subcommands:
                return  # menus don't have subcommands you smooth brain

            selected_cmd = self.commands["context"][cmd_name]

            if (
                selected_cmd.allowed_guild_ids
                and ctx.guild_id not in selected_cmd.allowed_guild_ids
            ):
                return

            if selected_cmd.has_subcommands and not selected_cmd.func:
                return await self.handle_subcommand(ctx, to_use)

            if "options" in to_use["data"]:
                for x in to_use["data"]["options"]:
                    if "value" not in x:
                        return await self.handle_subcommand(ctx, to_use)

            self._discord.dispatch("context_menu", ctx)

            await self.invoke_command(selected_cmd, ctx, args={})

        # Cog Logic

        elif to_use["data"]["name"] in self.commands:
            ctx = context.MenuContext(self.req, to_use, self._discord, self.logger)
            cmd_name = to_use["data"]["name"]

            if cmd_name not in self.commands and cmd_name in self.subcommands:
                return  # menus don't have subcommands you smooth brain

            selected_cmd = self.commands[cmd_name]
            if type(selected_cmd) == dict:
                return  # Get rid of any selection thats a dict somehow
            if selected_cmd._type == 1:  # noqa
                return  # Slash command obj.

            if (
                selected_cmd.allowed_guild_ids
                and ctx.guild_id not in selected_cmd.allowed_guild_ids
            ):
                return

            if selected_cmd.has_subcommands and not selected_cmd.func:
                return await self.handle_subcommand(ctx, to_use)

            if "options" in to_use["data"]:
                for x in to_use["data"]["options"]:
                    if "value" not in x:
                        return await self.handle_subcommand(ctx, to_use)

            self._discord.dispatch("context_menu", ctx)

            await self.invoke_command(selected_cmd, ctx, args={})

    async def handle_subcommand(self, ctx: context.SlashContext, data: dict):
        """
        Coroutine for handling subcommand.

        .. warning::
            Do not manually call this.

        :param ctx: :class:`.model.SlashContext` instance.
        :param data: Gateway message.
        """
        if data["data"]["name"] not in self.subcommands:
            return
        base = self.subcommands[data["data"]["name"]]
        sub = data["data"]["options"][0]
        sub_name = sub["name"]
        if sub_name not in base:
            return
        ctx.subcommand_name = sub_name
        sub_opts = sub["options"] if "options" in sub else []
        for x in sub_opts:
            if "options" in x or "value" not in x:
                sub_group = x["name"]
                if sub_group not in base[sub_name]:
                    return
                ctx.subcommand_group = sub_group
                selected = base[sub_name][sub_group]

                # This is to temporarily fix Issue #97, that on Android device
                # does not give option type from API.
                temporary_auto_convert = {}
                for n in selected.options:
                    temporary_auto_convert[n["name"].lower()] = n["type"]

                args = (
                    await self.process_options(
                        ctx.guild, x["options"], selected.connector, temporary_auto_convert
                    )
                    if "options" in x
                    else {}
                )
                self._discord.dispatch("slash_command", ctx)
                await self.invoke_command(selected, ctx, args)
                return
        selected = base[sub_name]

        # This is to temporarily fix Issue #97, that on Android device
        # does not give option type from API.
        temporary_auto_convert = {}
        for n in selected.options:
            temporary_auto_convert[n["name"].lower()] = n["type"]

        args = (
            await self.process_options(
                ctx.guild, sub_opts, selected.connector, temporary_auto_convert
            )
            if "options" in sub
            else {}
        )
        self._discord.dispatch("slash_command", ctx)
        await self.invoke_command(selected, ctx, args)

    def _on_error(self, ctx, ex, event_name):
        on_event = "on_" + event_name
        if self.has_listener:
            if self._discord.extra_events.get(on_event):
                self._discord.dispatch(event_name, ctx, ex)
                return True
        if hasattr(self._discord, on_event):
            self._discord.dispatch(event_name, ctx, ex)
            return True
        return False

    async def on_slash_command_error(self, ctx, ex):
        """
        Handles Exception occurred from invoking command.

        Example of adding event:

        .. code-block:: python

            @client.event
            async def on_slash_command_error(ctx, ex):
                ...

        Example of adding listener:

        .. code-block:: python

            @bot.listen()
            async def on_slash_command_error(ctx, ex):
                ...

        :param ctx: Context of the command.
        :type ctx: :class:`.model.SlashContext`
        :param ex: Exception from the command invoke.
        :type ex: Exception
        :return:
        """
        if not self._on_error(ctx, ex, "slash_command_error"):
            # Prints exception if not overridden or has no listener for error.
            self.logger.exception(
                f"An exception has occurred while executing command `{ctx.name}`:"
            )

    async def on_component_callback_error(self, ctx, ex):
        """
        Handles Exception occurred from invoking component callback.

        Example of adding event:

        .. code-block:: python

            @client.event
            async def on_component_callback_error(ctx, ex):
                ...

        Example of adding listener:

        .. code-block:: python

            @bot.listen()
            async def on_component_callback_error(ctx, ex):
                ...

        :param ctx: Context of the callback.
        :type ctx: :class:`.model.ComponentContext`
        :param ex: Exception from the command invoke.
        :type ex: Exception
        :return:
        """
        if not self._on_error(ctx, ex, "component_callback_error"):
            # Prints exception if not overridden or has no listener for error.
            self.logger.exception(
                f"An exception has occurred while executing component callback custom ID `{ctx.custom_id}`:"
            )
