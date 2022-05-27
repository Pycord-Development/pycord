# This example requires the 'members' privileged intent to use the Member converter.

import discord
from discord.commands import CommandPermission, SlashCommandGroup
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = discord.Bot(debug_guilds=[...], intents=intents, owner_id=...)  # Main file


class Example(commands.Cog):
    def __init__(self, bot_: discord.Bot):
        self.bot = bot_

    greetings = SlashCommandGroup("greetings", "Various greeting from cogs!")

    international_greetings = greetings.create_subgroup("international", "International greetings")

    secret_greetings = SlashCommandGroup(
        "secret_greetings",
        "Secret greetings",
        permissions=[CommandPermission("owner", 2, True)],  # Ensures the owner_id user can access this, and no one else
    )

    @greetings.command()
    async def hello(self, ctx: discord.ApplicationContext):
        await ctx.respond("Hello, this is a slash subcommand from a cog!")

    @international_greetings.command()
    async def aloha(self, ctx: discord.ApplicationContext):
        await ctx.respond("Aloha, a Hawaiian greeting")

    @secret_greetings.command()
    async def secret_handshake(self, ctx: discord.ApplicationContext, member: discord.Member):
        await ctx.respond(f"{member.mention} secret handshakes you")


bot.add_cog(Example(bot))  # Put in a setup function for cog files
bot.run("TOKEN")  # Main file
