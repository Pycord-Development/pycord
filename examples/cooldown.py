import discord
from discord.ext import commands

bot = commands.Bot()


# an application command with cooldown
@bot.slash_command()
@commands.cooldown(1, 5, commands.BucketType.user)  # the command can only be used once in 5 seconds
async def slash(ctx):
    await ctx.respond("You can't use this command again in 5 seconds.")


# error handler
@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond("This command is currently on cooldown.")
    else:
        raise error  # raise other errors so they aren't ignored


# a prefixed command with cooldown
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def prefixed(ctx):
    await ctx.send("You can't use this command again in 5 seconds.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("This command is currently on cooldown.")
    else:
        raise error
