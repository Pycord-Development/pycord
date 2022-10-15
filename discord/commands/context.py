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

from typing import TYPE_CHECKING, Any, TypeVar

import discord.abc
from discord.interactions import Interaction, InteractionMessage, InteractionResponse
from discord.webhook.async_ import Webhook
from .mixins import BaseContext

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    import discord
    from .. import Bot

    from .core import ApplicationCommand, Option
    from ..interactions import InteractionChannel
    from ..message import Message
    from ..permissions import Permissions
    from ..client import ClientUser

    from ..cog import Cog
    from ..webhook import WebhookMessage

    from typing import Callable, Awaitable

from ..utils import cached_property

T = TypeVar("T")
CogT = TypeVar("CogT", bound="Cog")

if TYPE_CHECKING:
    P = ParamSpec("P")
else:
    P = TypeVar("P")

__all__ = ("ApplicationContext", "AutocompleteContext")


class ApplicationContext(BaseContext):
    """Represents a Discord application command interaction context.

    This class is not created manually and is instead passed to application
    commands as the first parameter.

    .. versionadded:: 2.0

    Attributes
    ----------
    bot: :class:`.Bot`
        The bot that the command belongs to.
    interaction: :class:`.Interaction`
        The interaction object that invoked the command.
    command: :class:`.ApplicationCommand`
        The command that this context belongs to.
    """
    command: Optional[ApplicationCommand]

    def __init__(
        self,
        bot: Bot,
        interaction: Interaction,
        *,
        command: Optional[ApplicationCommand] = None,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        **kwargs2
    ):
        super().__init__(bot=bot, command=command, args=args, kwargs=kwargs, **kwargs2)

        self.interaction = interaction

        # below attributes will be set after initialization
        self.focused: Option = None  # type: ignore
        self.value: str = None  # type: ignore
        self.options: dict = None  # type: ignore

    async def reinvoke(self, *, call_hooks: bool = False, restart: bool = True) -> None:
        """|coro|

        Calls the command again.

        This is similar to :meth:`~.BaseContext.invoke` except that it bypasses
        checks, cooldowns, and error handlers.

        .. note::

            If you want to bypass :exc:`.UserInputError` derived exceptions,
            it is recommended to use the regular :meth:`~.Context.invoke`
            as it will work more naturally. After all, this will end up
            using the old arguments the user has used and will thus just
            fail again.

        Parameters
        ----------
        call_hooks: :class:`bool`
            Whether to call the before and after invoke hooks.
        restart: :class:`bool`
            Whether to start the call chain from the very beginning
            or where we left off (i.e. the command that caused the error).
            The default is to start where we left off.

        Raises
        -------
        ValueError
            The context to reinvoke is not valid.
        """
        cmd = self.command
        if cmd is None:
            raise ValueError("This context is not valid.")

        if restart:
            to_call = cmd.root_parent or cmd
        else:
            to_call = cmd

        try:
            await to_call.reinvoke(self, call_hooks=call_hooks)
        finally:
            self.command = cmd

    @property
    def source(self) -> Interaction:
        return self.interaction

    @cached_property
    def locale(self) -> str | None:
        """:class:`str`: Returns the locale of the guild associated with this context's command.
        Shorthand for :attr:`.Interaction.locale`.
        """
        return self.interaction.locale

    @cached_property
    def guild_locale(self) -> str | None:
        """:class:`str`: Returns the locale of the guild associated with this context's command.
        Shorthand for :attr:`.Interaction.guild_locale`.
        """
        return self.interaction.guild_locale

    @cached_property
    def app_permissions(self) -> Permissions:
        return self.interaction.app_permissions

    @cached_property
    def message(self) -> Message | None:
        """Optional[:class:`.Message`]: Returns the message sent with this context's command.
        Shorthand for :attr:`.Interaction.message`, if applicable.
        """
        return self.interaction.message

    @cached_property
    def response(self) -> InteractionResponse:
        """:class:`.InteractionResponse`: Returns the response object associated with this context's command.
        Shorthand for :attr:`.Interaction.response`.
        """
        return self.interaction.response

    @property
    def selected_options(self) -> list[dict[str, Any]] | None:
        """The options and values that were selected by the user when sending the command.

        Returns
        -------
        Optional[List[Dict[:class:`str`, Any]]]
            A dictionary containing the options and values that were selected by the user when the command
            was processed, if applicable. Returns ``None`` if the command has not yet been invoked,
            or if there are no options defined for that command.
        """
        return self.interaction.data.get("options", None)

    @property
    def unselected_options(self) -> list[Option] | None:
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
                    if option.to_dict()["name"]
                    not in [opt["name"] for opt in self.selected_options]
                ]
            else:
                return self.command.options  # type: ignore
        return None

    @property
    @discord.utils.copy_doc(InteractionResponse.send_modal)
    def send_modal(self) -> Callable[..., Awaitable[Interaction]]:
        return self.interaction.response.send_modal

    async def respond(self, *args, **kwargs) -> Interaction | WebhookMessage:
        """|coro|

        Sends either a response or a message using the followup webhook determined by whether the interaction
        has been responded to or not.

        Returns
        -------
        Union[:class:`discord.Interaction`, :class:`discord.WebhookMessage`]:
            The response, its type depending on whether it's an interaction response or a followup.
        """
        try:
            if not self.interaction.response.is_done():
                return await self.interaction.response.send_message(
                    *args, **kwargs
                )  # self.response
            else:
                return await self.followup.send(*args, **kwargs)  # self.send_followup
        except discord.errors.InteractionResponded:
            return await self.followup.send(*args, **kwargs)

    @property
    @discord.utils.copy_doc(InteractionResponse.send_message)
    def send_response(self) -> Callable[..., Awaitable[Interaction]]:
        if not self.interaction.response.is_done():
            return self.interaction.response.send_message
        else:
            raise RuntimeError(
                f"Interaction was already issued a response. Try using {type(self).__name__}.send_followup() instead."
            )

    @property
    @discord.utils.copy_doc(Webhook.send)
    def send_followup(self) -> Callable[..., Awaitable[WebhookMessage]]:
        if self.interaction.response.is_done():
            return self.followup.send
        else:
            raise RuntimeError(
                f"Interaction was not yet issued a response. Try using {type(self).__name__}.respond() first."
            )

    @property
    @discord.utils.copy_doc(InteractionResponse.defer)
    def defer(self) -> Callable[..., Awaitable[None]]:
        return self.interaction.response.defer

    @property
    def followup(self) -> Webhook:
        """:class:`Webhook`: Returns the followup webhook for followup interactions."""
        return self.interaction.followup

    async def delete(self, *, delay: float | None = None) -> None:
        """|coro|

        Deletes the original interaction response message.

        This is a higher level interface to :meth:`Interaction.delete_original_response`.

        Parameters
        ----------
        delay: Optional[:class:`float`]
            If provided, the number of seconds to wait before deleting the message.

        Raises
        ------
        HTTPException
            Deleting the message failed.
        Forbidden
            You do not have proper permissions to delete the message.
        """
        if not self.interaction.response.is_done():
            await self.defer()

        return await self.interaction.delete_original_response(delay=delay)

    @property
    @discord.utils.copy_doc(Interaction.edit_original_response)
    def edit(self) -> Callable[..., Awaitable[InteractionMessage]]:
        return self.interaction.edit_original_response


class AutocompleteContext:
    """Represents context for a slash command's option autocomplete. This ***does not*** inherent from :class:`.BaseContext`.

    This class is not created manually and is instead passed to an :class:`.Option`'s autocomplete callback.

    .. versionadded:: 2.0

    Attributes
    ----------
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
    options: Dict[:class:`str`, Any]
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
    def cog(self) -> Cog | None:
        """Optional[:class:`.Cog`]: Returns the cog associated with this context's command.
        ``None`` if it does not exist.
        """
        if self.command is None:
            return None

        return self.command.cog
