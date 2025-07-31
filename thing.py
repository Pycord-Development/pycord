import discord
import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = discord.Bot(intents=discord.Intents.default())


@bot.command()
async def ping(ctx: discord.ApplicationContex) -> None:
    await ctx.respond("slurp")
