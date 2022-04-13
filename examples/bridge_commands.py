import asyncio

import discord

from discord.ext import bridge

intents = discord.Intents.default()
intents.message_content = True

bot = bridge.Bot(command_prefix="!", intents=intents)


@bot.bridge_command()
async def ping(ctx):
    await ctx.respond("Pong!")


@bot.bridge_command()
@discord.option(name="value", choices=[1, 2, 3])
async def choose(ctx, value: int):
    await ctx.respond(f"You chose: {value}!")


@bot.bridge_command()
async def welcome(ctx, member: discord.Member):
    await ctx.respond(f"Welcome {member.mention}!")


@bot.bridge_command()
@discord.option(name="seconds", choices=range(1, 11))
async def wait(ctx, seconds: int = 5):
    await ctx.defer()
    await asyncio.sleep(seconds)
    await ctx.respond(f"Waited for {seconds} seconds!")


bot.run("TOKEN")
