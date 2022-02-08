import discord
from discord.commands import slash_command, ApplicationContext

class SlashExample(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        guild_ids=[...], name="ping", description="check the latency of the bot!"
    )
    async def ping(self, ctx: ApplicationContext):
        """
        ephemeral makes "Only you can see this" message

        `await ctx.respond(f"{round(self.client.latency * 1000)}ms",ephemeral=True)`
        """
        return await ctx.respond(f"{round(self.client.latency * 1000)}ms")

    @ping.error
    async def ping_error(self, ctx: ApplicationContext, error):
        return await ctx.respond(
            error, ephemeral=True
        )  # ephemeral makes "Only you can see this" message


def setup(bot):
    bot.add_cog(SlashExample(bot))
