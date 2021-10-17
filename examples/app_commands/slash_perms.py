import discord

# Imports Commands from discord.app (for Slash Permissions)
from discord.app import commands

bot = discord.Bot()

# Note: If you want you can use commands.Bot instead of discord.Bot
# Use discord.Bot if you don't want prefixed message commands

# With discord.Bot you can use @bot.command as an alias 
# of @bot.slash_command but this is overridden by commands.Bot

# by default, default_permission is set to True, you can use
# default_permission=False to disable the command for everyone.
# You can add up to 10 permissions per Global / Guild Command.
# @commands.has_role("ROLE_NAME") <-- can use either a name or id
# @commands.has_any_role("ROLE_NAME", "ROLE_NAME_2") <-- can use either a name or id
# @commands.is_user(USER_ID) <-- id only
# @commands.is_owner()

# Note: Please replace token, GUILD_ID, USER_ID and ROLE_NAME.

# Guild Slash Command Example with User Permissions
@bot.slash_command(guild_ids=[GUILD_ID], default_permission=False)
@commands.is_user(USER_ID)
async def user(ctx):
    """Say hello to the author"""  # the command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")

# Guild Slash Command Example with Owner Permissions
@bot.slash_command(guild_ids=[GUILD_ID], default_permission=False)
@commands.is_owner()
async def owner(ctx):
    """Say hello to the author"""  # the command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")

# Guild Slash Command Example with Role Permissions
@bot.slash_command(guild_ids=[GUILD_ID], default_permission=False)
@commands.has_role("ROLE_NAME")
async def role(ctx):
    """Say hello to the author"""  # the command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")

# Guild Slash Command Example with Any Specified Role Permissions
@bot.slash_command(guild_ids=[GUILD_ID], default_permission=False)
@commands.has_any_role("ROLE_NAME", "ROLE_NAME2")
async def multirole(ctx):
    """Say hello to the author"""  # the command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")

# To learn how to add descriptions, choices to options check slash_options.py
bot.run("token")