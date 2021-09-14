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

from typing import TYPE_CHECKING, Optional, Union

import discord.abc

if TYPE_CHECKING:
    import discord
    from discord.state import ConnectionState

from ..guild import Guild
from ..interactions import Interaction, InteractionResponse
from ..member import Member
from ..message import Message
from ..user import User
from ..utils import cached_property


class ApplicationContext(discord.abc.Messageable):
    """Represents a Discord interaction context.

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

    def __init__(self, bot: "discord.Bot", interaction: Interaction):
        self.bot = bot
        self.interaction = interaction
        self.command = None
        self._state: ConnectionState = self.interaction._state

    async def _get_channel(self) -> discord.abc.Messageable:
        return self.channel

    @cached_property
    def channel(self):
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
    def message(self) -> Optional[Message]:
        return self.interaction.message

    @cached_property
    def user(self) -> Optional[Union[Member, User]]:
        return self.interaction.user

    @property
    def voice_client(self):
        return self.guild.voice_client

    @cached_property
    def response(self) -> InteractionResponse:
        return self.interaction.response

    author = user

    @property
    def respond(self):
        return self.followup.send if self.response.is_done() else self.interaction.response.send_message

    @property
    def defer(self):
        return self.interaction.response.defer

    @property
    def followup(self):
        return self.interaction.followup

    async def delete(self):
        """Calls :attr:`~discord.app.ApplicationContext.respond`.
        If the response is done, then calls :attr:`~discord.app.ApplicationContext.respond` first."""
        if not self.response.is_done():
            await self.defer()

        return await self.interaction.delete_original_message()

    @property
    def edit(self):
        return self.interaction.edit_original_message
