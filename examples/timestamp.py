import discord
from discord.ext import commands
from discord import TimestampType

from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True  # < This may give you `read-only` warning, just ignore it.
# This intent requires "Message Content Intent" to be enabled at https://discord.com/developers


bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print('Ready!')

@bot.command()
async def created(ctx):
    timestamp = discord.Timestamp(value=ctx.author.created_at, type=TimestampType.LONG_DATETIME)
    await ctx.send(f'Your account was created: {timestamp}')


bot.run("TOKEN")