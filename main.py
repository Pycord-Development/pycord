from os import getenv

import discord
from discord.ext import bridge, commands


class MyCog(commands.Cog):
    @discord.command()
    async def slash_command(self, ctx):
        await ctx.respond("Hi")

    @commands.command()
    async def prefix_command(self, ctx):
        await ctx.respond("Hi")

    @bridge.bridge_command()
    async def bridge_command(self, ctx):
        await ctx.respond("Hi")

    @bridge.bridge_command()
    async def test(self, ctx):
        await ctx.respond("Hi")


bot = bridge.Bot()
bot.add_cog(MyCog())

bot.run(getenv("TOKEN"))
