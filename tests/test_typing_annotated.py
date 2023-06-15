from typing import Optional

import pytest
from typing_extensions import Annotated

import discord
from discord import ApplicationContext
from discord.commands.core import SlashCommand, slash_command


def test_typing_annotated():
    async def echo(ctx, txt: Annotated[str, discord.Option()]):
        await ctx.respond(txt)

    cmd = SlashCommand(echo)
    bot = discord.Bot()
    bot.add_application_command(cmd)


def test_typing_annotated_decorator():
    bot = discord.Bot()

    @bot.slash_command()
    async def echo(ctx, txt: Annotated[str, discord.Option(description="Some text")]):
        await ctx.respond(txt)


def test_typing_annotated_cog():
    class echoCog(discord.Cog):
        def __init__(self, bot_) -> None:
            self.bot = bot_
            super().__init__()

        @slash_command()
        async def echo(
            self, ctx, txt: Annotated[str, discord.Option(description="Some text")]
        ):
            await ctx.respond(txt)

    bot = discord.Bot()
    bot.add_cog(echoCog(bot))


def test_typing_annotated_cog_slashgroup():
    class echoCog(discord.Cog):
        grp = discord.commands.SlashCommandGroup("echo")

        def __init__(self, bot_) -> None:
            self.bot = bot_
            super().__init__()

        @grp.command()
        async def echo(
            self, ctx, txt: Annotated[str, discord.Option(description="Some text")]
        ):
            await ctx.respond(txt)

    bot = discord.Bot()
    bot.add_cog(echoCog(bot))


def test_typing_annotated_optional():
    async def echo(ctx, txt: Annotated[Optional[str], discord.Option()]):
        await ctx.respond(txt)

    cmd = SlashCommand(echo)
    bot = discord.Bot()
    bot.add_application_command(cmd)


def test_no_annotation():
    async def echo(ctx, txt: str):
        await ctx.respond(txt)

    cmd = SlashCommand(echo)
    bot = discord.Bot()
    bot.add_application_command(cmd)


def test_annotated_no_option():
    async def echo(ctx, txt: Annotated[str, "..."]):
        await ctx.respond(txt)

    cmd = SlashCommand(echo)
    bot = discord.Bot()
    bot.add_application_command(cmd)
