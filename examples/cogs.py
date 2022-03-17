# This will be your cog file inside the "cogs" folder

# cogs/whatever.py

from discord.ext commands

class MyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # basic ping command
    @commands.command #since we can't use bot (Will return error: "bot is not defined" we use "commands.command"
    async def ping(self, ctx: commands.Context):
        await ctx.send("Pong!")

    # command group "test"
    @commands.group()
    async def test(self, ctx: commands.Context):
        pass

    # ping command of group "test"
    @test.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send("Pong!")

def setup(bot):
    bot.add_cog(MyCog(bot)) # the setup function for the cog

# Main file Eg: "bot.py:

from discord.ext import commands

bot = commands.Bot(command_prefix="!")

bot.load_extension("whatever") # load the whatever.py

bot.run("token")
    
