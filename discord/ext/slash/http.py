import json
import typing

import aiohttp
import discord
from discord.http import Route

from . import error
from .const import BASE_API


class CustomRoute(Route):
    """discord.py's Route but changed ``BASE`` to use at slash command."""

    BASE = BASE_API


class SlashCommandRequest:
    def __init__(self, logger, _discord, application_id):
        self.logger = logger
        self._discord: typing.Union[discord.Client, discord.AutoShardedClient] = _discord
        self._application_id = application_id

    @property
    def application_id(self):
        return self._application_id or self._discord.user.id

    def put_slash_commands(self, slash_commands: list, guild_id):
        """
        Sends a slash command put request to the Discord API

        ``slash_commands`` must contain all the commands

        :param slash_commands: List of all the slash commands to make a put request to discord with.
        :param guild_id: ID of the guild to set the commands on. Pass `None` for the global scope.
        """
        return self.command_request(method="PUT", guild_id=guild_id, json=slash_commands)

    def remove_slash_command(self, guild_id, cmd_id):
        """
        Sends a slash command delete request to Discord API.

        :param guild_id: ID of the guild to remove command. Pass `None` to remove global command.
        :param cmd_id: ID of the command.
        :return: Response code of the request.
        """
        return self.command_request(method="DELETE", guild_id=guild_id, url_ending=f"/{cmd_id}")

    def get_all_commands(self, guild_id=None):
        """
        Sends a slash command get request to Discord API for all commands.

        :param guild_id: ID of the guild to get commands. Pass `None` to get global commands.
        :return: JSON Response of the request.
        """
        return self.command_request(method="GET", guild_id=guild_id)

    def get_all_guild_commands_permissions(self, guild_id):
        """
        Sends a slash command get request to Discord API for all permissions of a guild.

        :param guild_id: ID of the target guild to get registered command permissions of.
        :return: JSON Response of the request.
        """
        return self.command_request(method="GET", guild_id=guild_id, url_ending="/permissions")

    def update_guild_commands_permissions(self, guild_id, perms_dict):
        """
        Sends a slash command put request to the Discord API for setting all command permissions of a guild.

        :param guild_id: ID of the target guild to register command permissions.
        :return: JSON Response of the request.
        """
        return self.command_request(
            method="PUT", guild_id=guild_id, json=perms_dict, url_ending="/permissions"
        )

    def add_slash_command(
        self, guild_id, cmd_name: str, description: str, options: list = None, context: dict = None
    ):
        """
        Sends a slash command add request to Discord API.

        :param guild_id: ID of the guild to add command. Pass `None` to add global command.
        :param cmd_name: Name of the command. Must be match the regular expression ``^[a-z0-9_-]{1,32}$``.
        :param description: Description of the command.
        :param options: List of the function.
        :param context: Dictionary of context. Sends as separate.
        :return: JSON Response of the request.
        """
        base = {"name": cmd_name, "description": description, "options": options or []}
        if context:
            new_base = {"type": context["type"], "name": context["name"]}
            return self.command_request(json=new_base, method="POST", guild_id=guild_id)
        return self.command_request(json=base, method="POST", guild_id=guild_id)

    def command_request(self, method, guild_id, url_ending="", **kwargs):
        r"""
        Sends a command request to discord (post, get, delete, etc)

        :param method: HTTP method.
        :param guild_id: ID of the guild to make the request on. `None` to make a request on the global scope.
        :param url_ending: String to append onto the end of the url.
        :param \**kwargs: Kwargs to pass into discord.py's `request function <https://github.com/Rapptz/discord.py/blob/master/discord/http.py#L134>`_
        """
        url = f"/applications/{self.application_id}"
        url += "/commands" if not guild_id else f"/guilds/{guild_id}/commands"
        url += url_ending
        route = CustomRoute(method, url)
        return self._discord.http.request(route, **kwargs)

    def post_followup(self, _resp, token, files: typing.List[discord.File] = None):
        """
        Sends command followup response POST request to Discord API.

        :param _resp: Command response.
        :type _resp: dict
        :param token: Command message token.
        :param files: Files to send. Default ``None``
        :type files: List[discord.File]
        :return: Coroutine
        """
        if files:
            return self.request_with_files(_resp, files, token, "POST")
        return self.command_response(token, True, "POST", json=_resp)

    def post_initial_response(self, _resp, interaction_id, token):
        """
        Sends an initial "POST" response to the Discord API.

        :param _resp: Command response.
        :type _resp: dict
        :param interaction_id: Interaction ID.
        :param token: Command message token.
        :return: Coroutine
        """
        return self.command_response(token, False, "POST", interaction_id, json=_resp)

    def command_response(
        self, token, use_webhook, method, interaction_id=None, url_ending="", **kwargs
    ):
        r"""
        Sends a command response to discord (POST, PATCH, DELETE)

        :param token: Interaction token
        :param use_webhook: Whether to use webhooks
        :param method: The HTTP request to use
        :param interaction_id: The id of the interaction
        :param url_ending: String to append onto the end of the url.
        :param \**kwargs: Kwargs to pass into discord.py's `request function <https://github.com/Rapptz/discord.py/blob/master/discord/http.py#L134>`_
        :return: Coroutine
        """
        if not use_webhook and not interaction_id:
            raise error.IncorrectFormat(
                "Internal Error! interaction_id must be set if use_webhook is False"
            )
        req_url = (
            f"/webhooks/{self.application_id}/{token}"
            if use_webhook
            else f"/interactions/{interaction_id}/{token}/callback"
        )
        req_url += url_ending
        route = CustomRoute(method, req_url)
        return self._discord.http.request(route, **kwargs)

    def request_with_files(
        self, _resp, files: typing.List[discord.File], token, method, url_ending=""
    ):

        form = aiohttp.FormData()
        form.add_field("payload_json", json.dumps(_resp))
        for x in range(len(files)):
            name = f"file{x if len(files) > 1 else ''}"
            sel = files[x]
            form.add_field(
                name, sel.fp, filename=sel.filename, content_type="application/octet-stream"
            )
        return self.command_response(
            token, True, method, data=form, files=files, url_ending=url_ending
        )

    def edit(self, _resp, token, message_id="@original", files: typing.List[discord.File] = None):
        """
        Sends edit command response PATCH request to Discord API.

        :param _resp: Edited response.
        :type _resp: dict
        :param token: Command message token.
        :param message_id: Message ID to edit. Default initial message.
        :param files: Files. Default ``None``
        :type files: List[discord.File]
        :return: Coroutine
        """
        req_url = f"/messages/{message_id}"
        if files:
            return self.request_with_files(_resp, files, token, "PATCH", url_ending=req_url)
        return self.command_response(token, True, "PATCH", url_ending=req_url, json=_resp)

    def delete(self, token, message_id="@original"):
        """
        Sends delete command response POST request to Discord API.

        :param token: Command message token.
        :param message_id: Message ID to delete. Default initial message.
        :return: Coroutine
        """
        req_url = f"/messages/{message_id}"
        return self.command_response(token, True, "DELETE", url_ending=req_url)
