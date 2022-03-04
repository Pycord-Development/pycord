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

from typing import TYPE_CHECKING, Dict, List, Optional, TypeVar, Union

import discord.abc
from discord.interactions import InteractionMessage

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    import discord
    from .. import Bot
    from ..state import ConnectionState
    from ..voice_client import VoiceProtocol

    from .core import ApplicationCommand, Option
    from ..interactions import Interaction, InteractionResponse, InteractionChannel
    from ..guild import Guild
    from ..member import Member
    from ..message import Message
    from ..user import User
    from ..client import ClientUser
    from discord.webhook.async_ import Webhook

    from ..cog import Cog
    from ..webhook import WebhookMessage

    from typing import Callable, Awaitable

from ..utils import _cached_property as cached_property

T = TypeVar("T")
CogT = TypeVar("CogT", bound="Cog")

if TYPE_CHECKING:
    P = ParamSpec("P")
else:
    P = TypeVar("P")

__all__ = ("ApplicationContext", "AutocompleteContext")


class ApplicationContext(discord.abc.Messageable):
    """Represents a Discord application command interaction context.

    This class is not created manually and is instead passed to application
    commands as the first parameter.

    .. versionadded:: 2.0

    Attributes
    -----------
    bot: :class:`.Bot`
        The bot that the command belongs to.
    interaction: :class:`.Interaction`
        The interaction object that invoked the command.
    command: :class:`.ApplicationCommand`
        The command that this context belongs to.
    """

    def __init__(self, bot: Bot, interaction: Interaction):
        self.bot = bot
        self.interaction = interaction

        # below attributes will be set after initialization
        self.command: ApplicationCommand = None  # type: ignore
        self.focused: Option = None  # type: ignore
        self.value: str = None  # type: ignore
        self.options: dict = None  # type: ignore

        self._state: ConnectionState = self.interaction._state

    async def _get_channel(self) -> Optional[InteractionChannel]:
        return self.interaction.channel

    async def invoke(
        self,
        command: ApplicationCommand[CogT, P, T],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        r"""|coro|

        Calls a command with the arguments given.
        This is useful if you want to just call the callback that a
        :class:`.ApplicationCommand` holds internally.

        .. note::

            This does not handle converters, checks, cooldowns, pre-invoke,
            or after-invoke hooks in any matter. It calls the internal callback
            directly as-if it was a regular function.
            You must take care in passing the proper arguments when
            using this function.

        Parameters
        -----------
        command: :class:`.ApplicationCommand`
            The command that is going to be called.
        \*args
            The arguments to use.
        \*\*kwargs
            The keyword arguments to use.
        Raises
        -------
        TypeError
            The command argument to invoke is missing.
        """
        return await command(self, *args, **kwargs)

    @cached_property
    def channel(self) -> Optional[InteractionChannel]:
        return self.interaction.channel

    @cached_property
    def channel_id(self) -> Optional[int]:
        return self.interaction.channel_id

    @cached_property
    def guild(self) -> Optional[Guild]:
        return self.interaction.guild

    @cached_property
    def guild_id(self) -> Optional[int]:
        return self.interaction.guild_id

    @cached_property
    def locale(self) -> Optional[str]:
        return self.interaction.locale

    @cached_property
    def guild_locale(self) -> Optional[str]:
        return self.interaction.guild_locale

    @cached_property
    def me(self) -> Optional[Union[Member, ClientUser]]:
        return self.interaction.guild.me if self.interaction.guild is not None else self.bot.user

    @cached_property
    def message(self) -> Optional[Message]:
        return self.interaction.message

    @cached_property
    def user(self) -> Optional[Union[Member, User]]:
        return self.interaction.user

    author: Optional[Union[Member, User]] = user

    @property
    def voice_client(self) -> Optional[VoiceProtocol]:
        if self.interaction.guild is None:
            return None

        return self.interaction.guild.voice_client

    @cached_property
    def response(self) -> InteractionResponse:
        return self.interaction.response

    @property
    def selected_options(self) -> Optional[List[Dict]]:
        """The options and values that were selected by the user when sending the command.

        Returns
        -------
        Optional[List[Dict]]
            A dictionary containing the options and values that were selected by the user when the command was processed, if applicable.
            Returns ``None`` if the command has not yet been invoked, or if there are no options defined for that command.
        """
        return self.interaction.data.get("options", None)

    @property
    def unselected_options(self) -> Optional[List[Option]]:
        """The options that were not provided by the user when sending the command.

        Returns
        -------
        Optional[List[:class:`.Option`]]
            A list of Option objects (if any) that were not selected by the user when the command was processed.
            Returns ``None`` if there are no options defined for that command.
        """
        if self.command.options is not None:  # type: ignore
            if self.selected_options:
                return [
                    option
                    for option in self.command.options  # type: ignore
                    if option.to_dict()["name"] not in [opt["name"] for opt in self.selected_options]
                ]
            else:
                return self.command.options  # type: ignore
        return None

    @property
    def send_modal(self) -> Interaction:
        """Sends a modal dialog to the user who invoked the interaction."""
        return self.interaction.response.send_modal

    @property
    def respond(self) -> Callable[..., Awaitable[Union[Interaction, WebhookMessage]]]:
        """Callable[..., Union[:class:`~.Interaction`, :class:`~.Webhook`]]: Sends either a response
        or a followup response depending on if the interaction has been responded to yet or not."""
        if not self.interaction.response.is_done():
            return self.interaction.response.send_message  # self.response
        else:
            return self.followup.send  # self.send_followup

    @property
    def send_response(self) -> Callable[..., Awaitable[Interaction]]:
        if not self.interaction.response.is_done():
            return self.interaction.response.send_message
        else:
            raise RuntimeError(
                f"Interaction was already issued a response. Try using {type(self).__name__}.send_followup() instead."
            )

    @property
    def send_followup(self) -> Callable[..., Awaitable[WebhookMessage]]:
        if self.interaction.response.is_done():
            return self.followup.send
        else:
            raise RuntimeError(
                f"Interaction was not yet issued a response. Try using {type(self).__name__}.respond() first."
            )

    @property
    def defer(self) -> Callable[..., Awaitable[None]]:
        return self.interaction.response.defer

    @property
    def followup(self) -> Webhook:
        return self.interaction.followup

    async def delete(self):
        """Calls :attr:`~discord.commands.ApplicationContext.respond`.
        If the response is done, then calls :attr:`~discord.commands.ApplicationContext.respond` first."""
        if not self.interaction.response.is_done():
            await self.defer()

        return await self.interaction.delete_original_message()

    @property
    def edit(self) -> Callable[..., Awaitable[InteractionMessage]]:
        return self.interaction.edit_original_message

    @property
    def cog(self) -> Optional[Cog]:
        """Optional[:class:`.Cog`]: Returns the cog associated with this context's command. ``None`` if it does not exist."""
        if self.command is None:
            return None

        return self.command.cog


class AutocompleteContext:
    """Represents context for a slash command's option autocomplete.

    This class is not created manually and is instead passed to an Option's autocomplete callback.

    .. versionadded:: 2.0

    Attributes
    -----------
    bot: :class:`.Bot`
        The bot that the command belongs to.
    interaction: :class:`.Interaction`
        The interaction object that invoked the autocomplete.
    command: :class:`.ApplicationCommand`
        The command that this context belongs to.
    focused: :class:`.Option`
        The option the user is currently typing.
    value: :class:`.str`
        The content of the focused option.
    options: :class:`.dict`
        A name to value mapping of the options that the user has selected before this option.
    """

    __slots__ = ("bot", "interaction", "command", "focused", "value", "options")

    def __init__(self, bot: Bot, interaction: Interaction):
        self.bot = bot
        self.interaction = interaction

        self.command: ApplicationCommand = None  # type: ignore
        self.focused: Option = None  # type: ignore
        self.value: str = None  # type: ignore
        self.options: dict = None  # type: ignore

    @property
    def cog(self) -> Optional[Cog]:
        """Optional[:class:`.Cog`]: Returns the cog associated with this context's command. ``None`` if it does not exist."""
        if self.command is None:
            return None

        return self.command.cog
