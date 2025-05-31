import discord
import os
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()

bot = commands.Bot()

@bot.slash_command()
async def hi(ctx: discord.ApplicationContext, name: str | None = "World"):
    """Say hi to someone."""
    await ctx.respond(f"Hello {name}!")

bot.run(os.getenv(("TOKEN_2")))