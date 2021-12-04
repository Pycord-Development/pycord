from discord.commands.permissions import Permission
import discord
from discord.commands.commands import SlashCommandGroup
from discord.ext import commands

# Set these
GUILD_ID=0
OWNER_ID=0

bot = discord.Bot(debug_guild=GUILD_ID, owner_id=OWNER_ID)

class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    greetings = SlashCommandGroup("greetings", "Various greeting from cogs!")
    international_greetings = greetings.command_group("international", "International greetings")

    secret_greetings = SlashCommandGroup("secret_greetings", "Secret greetings", permissions=[
        Permission("owner", 2, True) # Ensures the owner_id user can access this, and noone else
    ])
 
    @greetings.command()
    async def hello(self, ctx):
        await ctx.respond("Hi, this is a slash command from a cog!")

    @international_greetings.command()
    async def aloha(self, ctx):
        await ctx.respond("Aloha, a Hawaiian greeting")
    

    @greetings.command()
    async def hi(self, ctx):
        await ctx.respond(f"Hi, this is a slash sub-command from a cog!")

    @secret_greetings.command()
    async def secret_handshake(self, ctx, member: discord.Member):
        await ctx.respond(f"{member.mention} secret handshakes you")


bot.add_cog(Example(bot))


bot.run("TOKEN")
