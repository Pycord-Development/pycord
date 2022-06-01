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


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    # This is raised when a choice outside the given choices is selected on a prefixed command.
    if isinstance(error, commands.BadArgument):
        await ctx.reply("Hey! The valid choices are 1, 2, or 3!")
    else:
        raise error  # Raise other errors so they aren't ignored


bot.run("TOKEN")
