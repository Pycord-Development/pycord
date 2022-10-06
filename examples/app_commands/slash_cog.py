# This example demonstrates a standalone cog file with the bot instance in a separate file.

import discord
from discord.ext import commands


class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        guild_ids=[...]
    )  # Create a slash command for the supplied guilds.
    async def hello(self, ctx: discord.ApplicationContext):
        await ctx.respond("Hi, this is a slash command from a cog!")

    @commands.slash_command()  # Not passing in guild_ids creates a global slash command.
    async def hi(self, ctx: discord.ApplicationContext):
        await ctx.respond("Hi, this is a global slash command from a cog!")


def setup(bot):
    bot.add_cog(Example(bot))


# The basic bot instance in a separate file should look something like this:
# bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))
# bot.load_extension("slash_cog")
# bot.run("TOKEN")
