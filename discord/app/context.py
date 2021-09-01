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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import discord

from ..interactions import Interaction
from ..utils import cached_property


class InteractionContext:
    """Represents a Discord interaction context.
 
    This class is not created manually and is instead passed to application
    commands as the first parameter.

    .. versionadded:: 2.0
    """

    def __init__(self, bot: "discord.Bot", interaction: Interaction):
        self.bot = bot
        self.interaction = interaction

    @cached_property
    def channel(self):
        return self.interaction.channel

    @cached_property
    def channel_id(self):
        return self.interaction.channel_id

    @cached_property
    def guild(self):
        return self.interaction.guild

    @cached_property
    def guild_id(self):
        return self.interaction.guild_id

    @cached_property
    def message(self):
        return self.interaction.message

    @cached_property
    def user(self):
        return self.interaction.user

    @cached_property
    def response(self):
        return self.interaction.response

    author = user

    @property
    def respond(self):
        return self.interaction.response.send_message

    @property
    def send(self):
        return self.respond

    @property
    def defer(self):
        return self.interaction.response.defer

    @property
    def followup(self):
        return self.interaction.followup

