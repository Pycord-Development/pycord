"""Tests for :mod:`discord.commands.core`."""

import pytest

import discord


def _make_group() -> discord.SlashCommandGroup:
    return discord.SlashCommandGroup(
        name="music",
        description="Music commands",
        integration_types={discord.IntegrationType.guild_install},
    )


def _make_command() -> discord.SlashCommand:
    @discord.slash_command(
        integration_types={discord.IntegrationType.guild_install},
    )
    async def music(ctx):
        pass

    return music


@pytest.mark.parametrize("factory", [_make_group, _make_command])
def test_guild_only_without_contexts(factory):
    """`guild_only` must not raise when `contexts` was never supplied."""
    command = factory()
    assert command.contexts is None
    with pytest.warns(DeprecationWarning):
        assert command.guild_only is False


@pytest.mark.parametrize("factory", [_make_group, _make_command])
def test_guild_only_with_guild_context(factory):
    command = factory()
    command.contexts = {discord.InteractionContextType.guild}
    with pytest.warns(DeprecationWarning):
        assert command.guild_only is True
