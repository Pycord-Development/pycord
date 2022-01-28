from discord.ext import commands
from discord.commands import slash_command


class Temptests2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def testing838(self, ctx):
        await ctx.respond("Test for #838")
        self.bot.reload_extension("ext")


def setup(bot):
    bot.add_cog(Temptests2(bot))
