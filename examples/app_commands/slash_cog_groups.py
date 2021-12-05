import discord
from discord.commands import SlashCommandGroup, Permission
from discord.ext import commands

bot = discord.Bot(debug_guild=..., owner_id=...)  # main file


class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    greetings = SlashCommandGroup("greetings", "Various greeting from cogs!")

    international_greetings = greetings.create_subgroup(
        "international", "International greetings"
    )

    secret_greetings = SlashCommandGroup(
        "secret_greetings",
        "Secret greetings",
        permissions=[
            Permission(
                "owner", 2, True
            )  # Ensures the owner_id user can access this, and no one else
        ],
    )

    @greetings.command()
    async def hello(self, ctx):
        await ctx.respond("Hello, this is a slash subcommand from a cog!")

    @international_greetings.command()
    async def aloha(self, ctx):
        await ctx.respond("Aloha, a Hawaiian greeting")

    @secret_greetings.command()
    async def secret_handshake(self, ctx, member: discord.Member):
        await ctx.respond(f"{member.mention} secret handshakes you")


bot.add_cog(Example(bot))  # put in a setup function for cog files
bot.run("TOKEN")  # main file
