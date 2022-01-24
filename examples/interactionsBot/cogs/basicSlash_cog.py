import discord
from discord.commands import Option, slash_command
from discord.ext import commands
from discord.ext.commands.context import Context


class SlashExample(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        guild_ids=[...], name="ping", description="check the latency of the bot!"
    )
    async def ping(self, ctx):
        """
        ephemeral makes "Only you can see this" message

        `await ctx.respond(f"{round(self.client.latency * 1000)}ms",ephemeral=True)`
        """
        return await ctx.respond(f"{round(self.client.latency * 1000)}ms")

    @ping.error
    async def ping_error(self, ctx: Context, error):
        return await ctx.respond(
            error, ephemeral=True
        )  # ephemeral makes "Only you can see this" message


def setup(bot):
    bot.add_cog(SlashExample(bot))
