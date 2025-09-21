from typing import Optional

from typing_extensions import Annotated

import discord
from discord import SlashCommandOptionType
from discord.commands.core import SlashCommand, slash_command


def test_typing_annotated():
    async def echo(ctx, txt: Annotated[str, discord.Option()]):
        await ctx.respond(txt)

    cmd = SlashCommand(echo)
    bot = discord.Bot()
    bot.add_application_command(cmd)
    dict_result = cmd.to_dict()
    assert dict_result.get("options")[0].get("type") == SlashCommandOptionType.string.value


def test_typing_annotated_decorator():
    bot = discord.Bot()

    @bot.slash_command()
    async def echo(ctx, txt: Annotated[str, discord.Option(description="Some text")]):
        await ctx.respond(txt)

    dict_result = echo.to_dict()

    option = dict_result.get("options")[0]
    assert option.get("type") == SlashCommandOptionType.string.value
    assert option.get("description") == "Some text"


def test_typing_annotated_cog():
    class echoCog(discord.Cog):
        def __init__(self, bot_) -> None:
            self.bot = bot_
            super().__init__()

        @slash_command()
        async def echo(self, ctx, txt: Annotated[str, discord.Option(description="Some text")]):
            await ctx.respond(txt)

    bot = discord.Bot()
    cog = echoCog(bot)
    bot.add_cog(cog)

    dict_result = cog.echo.to_dict()

    option = dict_result.get("options")[0]
    assert option.get("type") == SlashCommandOptionType.string.value
    assert option.get("description") == "Some text"


def test_typing_annotated_cog_slashgroup():
    class echoCog(discord.Cog):
        grp = discord.commands.SlashCommandGroup("echo")

        def __init__(self, bot_) -> None:
            self.bot = bot_
            super().__init__()

        @grp.command()
        async def echo(self, ctx, txt: Annotated[str, discord.Option(description="Some text")]):
            await ctx.respond(txt)

    bot = discord.Bot()
    cog = echoCog(bot)
    bot.add_cog(cog)

    dict_result = cog.echo.to_dict()

    option = dict_result.get("options")[0]
    assert option.get("type") == SlashCommandOptionType.string.value
    assert option.get("description") == "Some text"


def test_typing_annotated_optional():
    async def echo(ctx, txt: Annotated[str | None, discord.Option()]):
        await ctx.respond(txt)

    cmd = SlashCommand(echo)
    bot = discord.Bot()
    bot.add_application_command(cmd)

    dict_result = cmd.to_dict()

    option = dict_result.get("options")[0]
    assert option.get("type") == SlashCommandOptionType.string.value


def test_no_annotation():
    async def echo(ctx, txt: str):
        await ctx.respond(txt)

    cmd = SlashCommand(echo)
    bot = discord.Bot()
    bot.add_application_command(cmd)

    dict_result = cmd.to_dict()

    option = dict_result.get("options")[0]
    assert option.get("type") == SlashCommandOptionType.string.value


def test_annotated_no_option():
    async def echo(ctx, txt: Annotated[str, "..."]):
        await ctx.respond(txt)

    cmd = SlashCommand(echo)
    bot = discord.Bot()
    bot.add_application_command(cmd)

    dict_result = cmd.to_dict()

    option = dict_result.get("options")[0]
    assert option.get("type") == SlashCommandOptionType.string.value
