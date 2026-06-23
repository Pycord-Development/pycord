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

import warnings

import pytest

import discord
from discord import SlashCommand, SlashCommandGroup
from discord.enums import InteractionContextType


async def _noop(ctx):
    pass


def _guild_only(command) -> bool:
    # ``guild_only`` is deprecated in favour of ``contexts``; the warning is
    # expected here and irrelevant to what we are asserting.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return command.guild_only


def _slash_command(**kwargs) -> SlashCommand:
    return SlashCommand(_noop, **kwargs)


# Regression test for https://github.com/Pycord-Development/pycord/issues/3282:
# reading ``guild_only`` raised ``TypeError`` when ``contexts`` was never set
# (e.g. when only ``integration_types`` was passed), because the getter used the
# ``in`` operator on ``None``.
def test_guild_only_is_false_when_contexts_is_unset():
    command = _slash_command(integration_types={discord.IntegrationType.user_install})

    assert command.contexts is None
    assert _guild_only(command) is False


def test_group_guild_only_is_false_when_contexts_is_unset():
    group = SlashCommandGroup("group", "description")

    assert group.contexts is None
    assert _guild_only(group) is False


def test_guild_only_is_true_for_guild_context_only():
    command = _slash_command(contexts={InteractionContextType.guild})

    assert _guild_only(command) is True


def test_guild_only_is_false_for_multiple_contexts():
    command = _slash_command(
        contexts={
            InteractionContextType.guild,
            InteractionContextType.bot_dm,
        }
    )

    assert _guild_only(command) is False


def test_guild_only_setter_round_trips():
    command = _slash_command(contexts={InteractionContextType.guild})

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        command.guild_only = False
        assert command.guild_only is False
        command.guild_only = True
        assert command.guild_only is True

    assert command.contexts == {InteractionContextType.guild}


def test_guild_only_emits_deprecation_warning():
    command = _slash_command(contexts={InteractionContextType.guild})

    with pytest.warns(DeprecationWarning):
        command.guild_only
