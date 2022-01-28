import discord
from discord.commands import slash_command, SlashCommandGroup
from discord.ext import commands


class Temptests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    gtest = SlashCommandGroup("gtest", "gtest")

    @gtest.command(name="dothing", description="gtest")
    async def gtest_dothing(self, ctx: discord.ApplicationContext):
        await ctx.respond("gtest_dothing")
        print(self.bot.application_commands)
        print(self.bot._application_commands)

    @slash_command(name="test838")
    async def test838(self, ctx: discord.ApplicationContext):
        """Test for #838"""
        await ctx.respond("Test for #838")
        self.bot.reload_extension("ext2")


def setup(bot):
    bot.add_cog(Temptests(bot))
    print('h')
