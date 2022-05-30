# This example requires the `message_content` privileged intent for prefixed commands.

import asyncio

import discord
from discord.ext import bridge, commands

intents = discord.Intents.default()
intents.message_content = True

bot = bridge.Bot(command_prefix=commands.when_mentioned_or("!"), debug_guilds=[...], intents=intents)


@bot.bridge_command()
async def ping(ctx: bridge.BridgeContext):
    await ctx.respond("Pong!")


@bot.bridge_command()
@discord.option(name="value", choices=[1, 2, 3])
async def choose(ctx: bridge.BridgeContext, value: int):
    await ctx.respond(f"You chose: {value}!")


@bot.bridge_command()
async def welcome(ctx: bridge.BridgeContext, member: discord.Member):
    await ctx.respond(f"Welcome {member.mention}!")


@bot.bridge_command()
@discord.option(name="seconds", choices=range(1, 11))
async def wait(ctx: bridge.BridgeContext, seconds: int = 5):
    await ctx.defer()
    await asyncio.sleep(seconds)
    await ctx.respond(f"Waited for {seconds} seconds!")


bot.run("TOKEN")
