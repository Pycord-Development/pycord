import inspect
import typing

import discord

from .error import IncorrectFormat, IncorrectGuildIDType
from .model import CogBaseCommandObject, CogComponentCallbackObject, CogSubcommandObject
from .utils import manage_commands
from .utils.manage_components import get_components_ids, get_messages_ids


def cog_slash(
    *,
    name: str = None,
    description: str = None,
    guild_ids: typing.List[int] = None,
    options: typing.List[dict] = None,
    default_permission: bool = True,
    permissions: typing.Dict[int, list] = None,
    connector: dict = None,
):
    """
    Decorator for Cog to add slash command.\n
    Almost same as :meth:`.client.SlashCommand.slash`.

    Example:

    .. code-block:: python

        class ExampleCog(commands.Cog):
            def __init__(self, bot):
                self.bot = bot

            @cog_ext.cog_slash(name="ping")
            async def ping(self, ctx: SlashContext):
                await ctx.send(content="Pong!")

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
    :param permissions: Dictionary of permissions of the slash command. Key being target guild_id and value being a list of permissions to apply. Default ``None``.
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

        desc = description or inspect.getdoc(cmd)
        if options is None:
            opts = manage_commands.generate_options(cmd, desc, connector)
        else:
            opts = options

        if guild_ids and not all(isinstance(item, int) for item in guild_ids):
            raise IncorrectGuildIDType(
                f"The snowflake IDs {guild_ids} given are not a list of integers. Because of discord.py convention, please use integer IDs instead. Furthermore, the command '{name or cmd.__name__}' will be deactivated and broken until fixed."
            )

        _cmd = {
            "func": cmd,
            "description": desc,
            "guild_ids": guild_ids,
            "api_options": opts,
            "default_permission": default_permission,
            "api_permissions": permissions,
            "connector": connector,
            "has_subcommands": False,
        }
        return CogBaseCommandObject(name or cmd.__name__, _cmd)

    return wrapper


def cog_subcommand(
    *,
    base,
    subcommand_group=None,
    name=None,
    description: str = None,
    base_description: str = None,
    base_desc: str = None,
    base_default_permission: bool = True,
    base_permissions: typing.Dict[int, list] = None,
    subcommand_group_description: str = None,
    sub_group_desc: str = None,
    guild_ids: typing.List[int] = None,
    options: typing.List[dict] = None,
    connector: dict = None,
):
    """
    Decorator for Cog to add subcommand.\n
    Almost same as :meth:`.client.SlashCommand.subcommand`.

    Example:

    .. code-block:: python

        class ExampleCog(commands.Cog):
            def __init__(self, bot):
                self.bot = bot

            @cog_ext.cog_subcommand(base="group", name="say")
            async def group_say(self, ctx: SlashContext, text: str):
                await ctx.send(content=text)

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
    :param base_permissions: Dictionary of permissions of the slash command. Key being target guild_id and value being a list of permissions to apply. Default ``None``.
    :type base_permissions: dict
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
    guild_ids = guild_ids if guild_ids else []
    if not base_permissions:
        base_permissions = {}

    def wrapper(cmd):
        decorator_permissions = getattr(cmd, "__permissions__", None)
        if decorator_permissions:
            base_permissions.update(decorator_permissions)

        desc = description or inspect.getdoc(cmd)
        if options is None:
            opts = manage_commands.generate_options(cmd, desc, connector)
        else:
            opts = options

        if guild_ids and not all(isinstance(item, int) for item in guild_ids):
            raise IncorrectGuildIDType(
                f"The snowflake IDs {guild_ids} given are not a list of integers. Because of discord.py convention, please use integer IDs instead. Furthermore, the command '{name or cmd.__name__}' will be deactivated and broken until fixed."
            )

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
            "name": name or cmd.__name__,
            "description": desc,
            "base_desc": base_description,
            "sub_group_desc": subcommand_group_description,
            "guild_ids": guild_ids,
            "api_options": opts,
            "connector": connector,
        }
        return CogSubcommandObject(base, _cmd, subcommand_group, name or cmd.__name__, _sub)

    return wrapper


# I don't feel comfortable with having these right now, they're too buggy even when they were working.


def cog_context_menu(*, name: str, guild_ids: list = None, target: int = 1):
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
        if name == "context":
            raise IncorrectFormat(
                "The name 'context' can not be used to register as a cog context menu,"
                "as this conflicts with this lib's checks. Please use a different name instead."
            )

        _cmd = {
            "default_permission": None,
            "has_permissions": None,
            "name": name,
            "type": target,
            "func": cmd,
            "description": "",
            "guild_ids": guild_ids,
            "api_options": [],
            "connector": {},
            "has_subcommands": False,
            "api_permissions": {},
        }
        return CogBaseCommandObject(name or cmd.__name__, _cmd, target)

    return wrapper


def permission(guild_id: int, permissions: list):
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


def cog_component(
    *,
    messages: typing.Union[int, discord.Message, list] = None,
    components: typing.Union[str, dict, list] = None,
    use_callback_name=True,
    component_type: int = None,
):
    """
    Decorator for component callbacks in cogs.\n
    Almost same as :meth:`.client.SlashCommand.component_callback`.

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

    def wrapper(callback):
        nonlocal custom_ids

        if use_callback_name and custom_ids == [None]:
            custom_ids = [callback.__name__]

        if message_ids == [None] and custom_ids == [None]:
            raise IncorrectFormat("You must specify messages or components (or both)")

        return CogComponentCallbackObject(
            callback,
            message_ids=message_ids,
            custom_ids=custom_ids,
            component_type=component_type,
        )

    return wrapper
