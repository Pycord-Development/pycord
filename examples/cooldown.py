# This example requires the `message_content` privileged intent for prefixed commands.

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", debug_guilds=[...], intents=intents)


# an application command with cooldown
@bot.slash_command()
@commands.cooldown(1, 5, commands.BucketType.user)  # the command can only be used once in 5 seconds
async def slash(ctx: discord.ApplicationContext):
    await ctx.respond("You can use this command again in 5 seconds.")


# application command error handler
@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond("This command is currently on cooldown.")
    else:
        raise error  # raise other errors so they aren't ignored


# a prefixed command with cooldown
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def prefixed(ctx: commands.Context):
    await ctx.send("You can use this command again in 5 seconds.")


# prefixed command error handler
@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("This command is currently on cooldown.")
    else:
        raise error


bot.run("TOKEN")
