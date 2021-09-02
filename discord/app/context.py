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

if TYPE_CHECKING:
    import discord

from ..abc import Messageable
from ..guild import Guild
from ..interactions import Interaction, InteractionResponse
from ..member import Member
from ..message import Message
from ..user import User
from ..utils import cached_property, copy_doc


class InteractionContext:
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

    @cached_property
    @copy_doc(Interaction.channel)
    def channel(self) -> Optional[int]:
        return self.interaction.channel

    @cached_property
    @copy_doc(Interaction.channel_id)
    def channel_id(self) -> Optional[int]:
        return self.interaction.channel_id

    @cached_property
    @copy_doc(Interaction.guild)
    def guild(self) -> Optional[Guild]:
        return self.interaction.guild

    @cached_property
    @copy_doc(Interaction.guild_id)
    def guild_id(self) -> Optional[int]:
        return self.interaction.guild_id

    @cached_property
    @copy_doc(Interaction.message)
    def message(self) -> Message:
        return self.interaction.message

    @cached_property
    @copy_doc(Interaction.user)
    def user(self) -> Optional[Union[Member, User]]:
        return self.interaction.user

    @cached_property
    @copy_doc(Interaction.response)
    def response(self) -> InteractionResponse:
        return self.interaction.response

    author = user

    @property
    @copy_doc(InteractionResponse.send_message)
    def respond(self):
        return self.interaction.response.send_message

    @property
    @copy_doc(Messageable.send)
    def send(self):
        return self.channel.send if self.response.is_done() else self.respond

    @property
    @copy_doc(InteractionResponse.defer)
    def defer(self):
        return self.interaction.response.defer

    @property
    @copy_doc(Interaction.followup)
    def followup(self):
        return self.interaction.followup

    @copy_doc(Interaction.delete_original_message)
    async def delete(self):
        if not self.response.is_done():
            await self.defer()

        return await self.interaction.delete_original_message()

    @property
    @copy_doc(Interaction.edit_original_message)
    def edit(self):
        return self.interaction.edit_original_message
