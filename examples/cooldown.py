# This example requires the `message_content` privileged intent for prefixed commands.

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), debug_guilds=[...], intents=intents)
bypassing_users = []  # used in the dynamic cooldown below

# An application command with cooldown
@bot.slash_command()
@commands.cooldown(1, 5, commands.BucketType.user)  # The command can only be used once in 5 seconds
async def slash(ctx: discord.ApplicationContext):
    await ctx.respond("You can use this command again in 5 seconds.")


# Application command error handler
@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond("This command is currently on cooldown.")
    else:
        raise error  # Raise other errors so they aren't ignored


# A prefixed command with cooldown
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def prefixed(ctx: commands.Context):
    await ctx.send("You can use this command again in 5 seconds.")


# Dynamic cooldown function; allows for custom cooldown logic such as different cooldowns per-user
def my_cooldown(message):
    if message.author.id in bypassing_users:
        return None  # Let specific users bypass the cooldown entirely
    elif message.author.get_role(929080208148017242):
        return commands.Cooldown(2, 5)  # Users with the above role ID can use the command twice in 5 seconds
    else:
        return commands.Cooldown(1, 10)  # All other users can use the command once in 10 seconds

# A prefixed command with the dynamic cooldown defined above
@bot.command()
@commands.dynamic_cooldown(my_cooldown, commands.BucketType.user)
async def dynamic(ctx: commands.Context):
    await ctx.send("You can use this command again soon.")


# Prefixed command error handler
@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("This command is currently on cooldown.")
    else:
        raise error


bot.run("TOKEN")
