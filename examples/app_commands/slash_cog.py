from discord.ext import commands
from discord.commands import slash_command

class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
 
    @slash_command()
    async def example(self, ctx):
        await ctx.respond("Hi, this is a slash command from a cog!")

def setup(bot):
    bot.add_cog(Example(bot))
