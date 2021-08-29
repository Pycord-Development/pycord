import asyncio
import inspect
import typing
from collections.abc import Callable
from typing import Union

import aiohttp

from ..error import IncorrectType, RequestFailure
from ..model import SlashCommandOptionType, SlashCommandPermissionType


async def add_slash_command(
    bot_id, bot_token: str, guild_id, cmd_name: str, description: str, options: list = None
):
    """
    A coroutine that sends a slash command add request to Discord API.

    :param bot_id: User ID of the bot.
    :param bot_token: Token of the bot.
    :param guild_id: ID of the guild to add command. Pass `None` to add global command.
    :param cmd_name: Name of the command. Must match the regular expression ``^[a-z0-9_-]{1,32}$``.
    :param description: Description of the command.
    :param options: List of the function.
    :return: JSON Response of the request.
    :raises: :class:`.error.RequestFailure` - Requesting to Discord API has failed.
    """
    url = f"https://discord.com/api/v8/applications/{bot_id}"
    url += "/commands" if not guild_id else f"/guilds/{guild_id}/commands"
    base = {"name": cmd_name, "description": description, "options": options or []}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, headers={"Authorization": f"Bot {bot_token}"}, json=base
        ) as resp:
            if resp.status == 429:
                _json = await resp.json()
                await asyncio.sleep(_json["retry_after"])
                return await add_slash_command(
                    bot_id, bot_token, guild_id, cmd_name, description, options
                )
            if not 200 <= resp.status < 300:
                raise RequestFailure(resp.status, await resp.text())
            return await resp.json()


async def remove_slash_command(bot_id, bot_token, guild_id, cmd_id):
    """
    A coroutine that sends a slash command remove request to Discord API.

    :param bot_id: User ID of the bot.
    :param bot_token: Token of the bot.
    :param guild_id: ID of the guild to remove command. Pass `None` to remove global command.
    :param cmd_id: ID of the command.
    :return: Response code of the request.
    :raises: :class:`.error.RequestFailure` - Requesting to Discord API has failed.
    """
    url = f"https://discord.com/api/v8/applications/{bot_id}"
    url += "/commands" if not guild_id else f"/guilds/{guild_id}/commands"
    url += f"/{cmd_id}"
    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers={"Authorization": f"Bot {bot_token}"}) as resp:
            if resp.status == 429:
                _json = await resp.json()
                await asyncio.sleep(_json["retry_after"])
                return await remove_slash_command(bot_id, bot_token, guild_id, cmd_id)
            if not 200 <= resp.status < 300:
                raise RequestFailure(resp.status, await resp.text())
            return resp.status


async def get_all_commands(bot_id, bot_token, guild_id=None):
    """
    A coroutine that sends a slash command get request to Discord API.

    :param bot_id: User ID of the bot.
    :param bot_token: Token of the bot.
    :param guild_id: ID of the guild to get commands. Pass `None` to get all global commands.
    :return: JSON Response of the request.
    :raises: :class:`.error.RequestFailure` - Requesting to Discord API has failed.
    """
    url = f"https://discord.com/api/v8/applications/{bot_id}"
    url += "/commands" if not guild_id else f"/guilds/{guild_id}/commands"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"Authorization": f"Bot {bot_token}"}) as resp:
            if resp.status == 429:
                _json = await resp.json()
                await asyncio.sleep(_json["retry_after"])
                return await get_all_commands(bot_id, bot_token, guild_id)
            if not 200 <= resp.status < 300:
                raise RequestFailure(resp.status, await resp.text())
            return await resp.json()


async def remove_all_commands(bot_id, bot_token, guild_ids: typing.List[int] = None):
    """
    Remove all slash commands.

    :param bot_id: User ID of the bot.
    :param bot_token: Token of the bot.
    :param guild_ids: List of the guild ID to remove commands. Pass ``None`` to remove only the global commands.
    """

    await remove_all_commands_in(bot_id, bot_token, None)

    for x in guild_ids or []:
        try:
            await remove_all_commands_in(bot_id, bot_token, x)
        except RequestFailure:
            pass


async def remove_all_commands_in(bot_id, bot_token, guild_id=None):
    """
    Remove all slash commands in area.

    :param bot_id: User ID of the bot.
    :param bot_token: Token of the bot.
    :param guild_id: ID of the guild to remove commands. Pass `None` to remove all global commands.
    """
    commands = await get_all_commands(bot_id, bot_token, guild_id)

    for x in commands:
        await remove_slash_command(bot_id, bot_token, guild_id, x["id"])


async def get_all_guild_commands_permissions(bot_id, bot_token, guild_id):
    """
    A coroutine that sends a gets all the commands permissions for that guild.

    :param bot_id: User ID of the bot.
    :param bot_token: Token of the bot.
    :param guild_id: ID of the guild to get permissions.
    :return: JSON Response of the request. A list of <https://discord.com/developers/docs/interactions/slash-commands#get-application-command-permissions>.
    :raises: :class:`.error.RequestFailure` - Requesting to Discord API has failed.
    """
    url = f"https://discord.com/api/v8/applications/{bot_id}/guilds/{guild_id}/commands/permissions"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"Authorization": f"Bot {bot_token}"}) as resp:
            if resp.status == 429:
                _json = await resp.json()
                await asyncio.sleep(_json["retry_after"])
                return await get_all_guild_commands_permissions(bot_id, bot_token, guild_id)
            if not 200 <= resp.status < 300:
                raise RequestFailure(resp.status, await resp.text())
            return await resp.json()


async def get_guild_command_permissions(bot_id, bot_token, guild_id, command_id):
    """
    A coroutine that sends a request to get a single command's permissions in guild

    :param bot_id: User ID of the bot.
    :param bot_token: Token of the bot.
    :param guild_id: ID of the guild to update permissions on.
    :param command_id: ID for the command to update permissions on.
    :return: JSON Response of the request. A list of <https://discord.com/developers/docs/interactions/slash-commands#edit-application-command-permissions>
    :raises: :class:`.error.RequestFailure` - Requesting to Discord API has failed.
    """
    url = f"https://discord.com/api/v8/applications/{bot_id}/guilds/{guild_id}/commands/{command_id}/permissions"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"Authorization": f"Bot {bot_token}"}) as resp:
            if resp.status == 429:
                _json = await resp.json()
                await asyncio.sleep(_json["retry_after"])
                return await get_guild_command_permissions(bot_id, bot_token, guild_id, command_id)
            if not 200 <= resp.status < 300:
                raise RequestFailure(resp.status, await resp.text())
            return await resp.json()


async def update_single_command_permissions(bot_id, bot_token, guild_id, command_id, permissions):
    """
    A coroutine that sends a request to update a single command's permissions in guild

    :param bot_id: User ID of the bot.
    :param bot_token: Token of the bot.
    :param guild_id: ID of the guild to update permissions on.
    :param command_id: ID for the command to update permissions on.
    :param permissions: List of permissions for the command.
    :return: JSON Response of the request. A list of <https://discord.com/developers/docs/interactions/slash-commands#edit-application-command-permissions>
    :raises: :class:`.error.RequestFailure` - Requesting to Discord API has failed.
    """
    url = f"https://discord.com/api/v8/applications/{bot_id}/guilds/{guild_id}/commands/{command_id}/permissions"
    async with aiohttp.ClientSession() as session:
        async with session.put(
            url, headers={"Authorization": f"Bot {bot_token}"}, json={"permissions": permissions}
        ) as resp:
            if resp.status == 429:
                _json = await resp.json()
                await asyncio.sleep(_json["retry_after"])
                return await update_single_command_permissions(
                    bot_id, bot_token, guild_id, command_id, permissions
                )
            if not 200 <= resp.status < 300:
                raise RequestFailure(resp.status, await resp.text())
            return await resp.json()


async def update_guild_commands_permissions(bot_id, bot_token, guild_id, cmd_permissions):
    """
    A coroutine that updates permissions for all commands in a guild.

    :param bot_id: User ID of the bot.
    :param bot_token: Token of the bot.
    :param guild_id: ID of the guild to update permissions.
    :param cmd_permissions: List of dict with permissions for each commands.
    :return: JSON Response of the request. A list of <https://discord.com/developers/docs/interactions/slash-commands#batch-edit-application-command-permissions>.
    :raises: :class:`.error.RequestFailure` - Requesting to Discord API has failed.
    """
    url = f"https://discord.com/api/v8/applications/{bot_id}/guilds/{guild_id}/commands/permissions"
    async with aiohttp.ClientSession() as session:
        async with session.put(
            url, headers={"Authorization": f"Bot {bot_token}"}, json=cmd_permissions
        ) as resp:
            if resp.status == 429:
                _json = await resp.json()
                await asyncio.sleep(_json["retry_after"])
                return await update_guild_commands_permissions(
                    bot_id, bot_token, guild_id, cmd_permissions
                )
            if not 200 <= resp.status < 300:
                raise RequestFailure(resp.status, await resp.text())
            return await resp.json()


def create_option(
    name: str,
    description: str,
    option_type: typing.Union[int, type],
    required: bool,
    choices: list = None,
) -> dict:
    """
    Creates option used for creating slash command.

    :param name: Name of the option.
    :param description: Description of the option.
    :param option_type: Type of the option.
    :param required: Whether this option is required.
    :param choices: Choices of the option. Can be empty.
    :return: dict

    .. note::
        An option with ``required=False`` will not pass anything to the command function if the user doesn't pass that option when invoking the command.
        You must set the the relevant argument's function to a default argument, eg ``argname = None``.

    .. note::
        ``choices`` must either be a list of `option type dicts <https://discord.com/developers/docs/interactions/slash-commands#applicationcommandoptionchoice>`_
        or a list of single string values.
    """
    if not isinstance(option_type, int) or isinstance(
        option_type, bool
    ):  # Bool values are a subclass of int
        original_type = option_type
        option_type = SlashCommandOptionType.from_type(original_type)
        if option_type is None:
            raise IncorrectType(
                f"The type {original_type} is not recognized as a type that Discord accepts for slash commands."
            )
    choices = choices or []
    choices = [
        choice if isinstance(choice, dict) else {"name": choice, "value": choice}
        for choice in choices
    ]
    return {
        "name": name,
        "description": description,
        "type": option_type,
        "required": required,
        "choices": choices,
    }


def generate_options(
    function: Callable, description: str = "No description.", connector: dict = None
) -> list:
    """
    Generates a list of options from the type hints of a command.
    You currently can type hint: str, int, bool, discord.User, discord.Channel, discord.Role

    .. warning::
        This is automatically used if you do not pass any options directly. It is not recommended to use this.

    :param function: The function callable of the command.
    :param description: The default argument description.
    :param connector: Kwargs connector of the command.
    """
    options = []
    if connector:
        connector = {y: x for x, y in connector.items()}  # Flip connector.
    params = iter(inspect.signature(function).parameters.values())
    if next(params).name in ("self", "cls"):
        # Skip 1. (+ 2.) parameter, self/cls and ctx
        next(params)

    for param in params:
        required = True
        if isinstance(param.annotation, str):
            # if from __future__ import annotations, then annotations are strings and should be converted back to types
            param = param.replace(annotation=eval(param.annotation, function.__globals__))

        if param.default is not inspect._empty:
            required = False
        elif getattr(param.annotation, "__origin__", None) is typing.Union:
            # Make a command argument optional with typing.Optional[type] or typing.Union[type, None]
            args = getattr(param.annotation, "__args__", None)
            if args:
                param = param.replace(annotation=args[0])
                required = not isinstance(args[-1], type(None))

        option_type = (
            SlashCommandOptionType.from_type(param.annotation) or SlashCommandOptionType.STRING
        )
        name = param.name if not connector else connector[param.name]
        options.append(create_option(name, description or "No Description.", option_type, required))

    return options


def create_choice(value: Union[str, int], name: str):
    """
    Creates choices used for creating command option.

    :param value: Value of the choice.
    :param name: Name of the choice.
    :return: dict
    """
    return {"value": value, "name": name}


def create_permission(
    id: int, id_type: typing.Union[int, SlashCommandPermissionType], permission: bool
):
    """
    Create a single command permission.

    :param id: Target id to apply the permission on.
    :param id_type: Type of the id, :class:`..model.SlashCommandPermissionsType`.
    :param permission: State of the permission. ``True`` to allow access, ``False`` to disallow access.
    :return: dict

    .. note::
        For @everyone permission, set id_type as role and id as guild id.
    """
    if not (
        isinstance(id_type, int) or isinstance(id_type, bool)
    ):  # Bool values are a subclass of int
        original_type = id_type
        id_type = SlashCommandPermissionType.from_type(original_type)
        if id_type is None:
            raise IncorrectType(
                f"The type {original_type} is not recognized as a type that Discord accepts for slash command permissions."
            )
    return {"id": id, "type": id_type, "permission": permission}


def create_multi_ids_permission(
    ids: typing.List[int], id_type: typing.Union[int, SlashCommandPermissionType], permission: bool
):
    """
    Creates a list of permissions from list of ids with common id_type and permission state.

    :param ids: List of target ids to apply the permission on.
    :param id_type: Type of the id.
    :param permission: State of the permission. ``True`` to allow access, ``False`` to disallow access.
    """
    return [create_permission(id, id_type, permission) for id in set(ids)]


def generate_permissions(
    allowed_roles: typing.List[int] = None,
    allowed_users: typing.List[int] = None,
    disallowed_roles: typing.List[int] = None,
    disallowed_users: typing.List[int] = None,
):
    """
    Creates a list of permissions.

    :param allowed_roles: List of role ids that can access command.
    :param allowed_users: List of user ids that can access command.
    :param disallowed_roles: List of role ids that should not access command.
    :param disallowed_users: List of users ids that should not access command.
    :return: list
    """
    permissions = []

    if allowed_roles:
        permissions.extend(
            create_multi_ids_permission(allowed_roles, SlashCommandPermissionType.ROLE, True)
        )
    if allowed_users:
        permissions.extend(
            create_multi_ids_permission(allowed_users, SlashCommandPermissionType.USER, True)
        )
    if disallowed_roles:
        permissions.extend(
            create_multi_ids_permission(disallowed_roles, SlashCommandPermissionType.ROLE, False)
        )
    if disallowed_users:
        permissions.extend(
            create_multi_ids_permission(disallowed_users, SlashCommandPermissionType.USER, False)
        )

    return permissions
