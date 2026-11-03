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

import discord
from discord import SlashCommandOptionType


def test_slash_command_option_type_union_user():
    # Resolves #3423: Member | User maps to SlashCommandOptionType.user
    assert (
        SlashCommandOptionType.from_datatype(discord.Member | discord.User)
        is SlashCommandOptionType.user
    )
    assert (
        SlashCommandOptionType.from_datatype(discord.User | discord.Member)
        is SlashCommandOptionType.user
    )


def test_slash_command_option_type_union_mentionable():
    # User | Role should map to mentionable
    assert (
        SlashCommandOptionType.from_datatype(discord.User | discord.Role)
        is SlashCommandOptionType.mentionable
    )
    assert (
        SlashCommandOptionType.from_datatype(discord.Member | discord.Role)
        is SlashCommandOptionType.mentionable
    )


def test_slash_command_option_type_union_channel():
    assert (
        SlashCommandOptionType.from_datatype(discord.TextChannel | discord.VoiceChannel)
        is SlashCommandOptionType.channel
    )
