import asyncio

import discord
from discord.ext import commands

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=discord.Intents.default(),
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@bot.slash_command(guild_ids=[...])  # Create a slash command.
async def hello(ctx: discord.ApplicationContext):
    """Say hello to the bot"""  # The command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author.mention}!")


async def main():
    async with bot:
        await bot.start("TOKEN")


asyncio.run(main())
