import discord
# Imports permissions from discord.commands
from discord.commands import permissions

bot = discord.Bot()

# Note: If you want you can use commands.Bot instead of discord.Bot
# Use discord.Bot if you don't want prefixed message commands

# With discord.Bot you can use @bot.command as an alias
# of @bot.slash_command but this is overridden by commands.Bot

# by default, default_permission is set to True, you can use
# default_permission=False to disable the command for everyone.
# You can add up to 10 permissions per Command for a guild.
# You can either use the following decorators:
# --------------------------------------------
# @permissions.permission(role_id/user_id, permission)
# @permissions.has_role("ROLE_NAME") <-- can use either a name or id
# @permissions.has_any_role("ROLE_NAME", "ROLE_NAME_2") <-- can use either a name or id
# @permissions.is_user(USER_ID) <-- id only
# @permissions.is_owner()
# Note: you can supply "guild_id" to limit it to 1 guild.
# Ex: @permissions.has_role("Admin", guild_id=GUILD_ID)
# --------------------------------------------
# or supply permissions directly in @bot.slash_command
# @bot.slash_command(default_permission=False,
#                   permissions=[permissions.Permission(id=ID, type=TYPE, permission=True, guild_id=GUILD_ID)])

# Note: Please replace token, GUILD_ID, USER_ID and ROLE_NAME.

# Guild Slash Command Example with User Permissions

GUILD_ID = ...
USER_ID = ...


@bot.slash_command(guild_ids=[GUILD_ID], default_permission=False)
@permissions.is_user(USER_ID)
async def user(ctx):
    """Say hello to the author"""  # the command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")


# Guild Slash Command Example with Owner Permissions
@bot.slash_command(guild_ids=[GUILD_ID], default_permission=False)
@permissions.is_owner()
async def owner(ctx):
    """Say hello to the author"""  # the command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")


# Guild Slash Command Example with Role Permissions
@bot.slash_command(guild_ids=[GUILD_ID], default_permission=False)
@permissions.has_role("ROLE_NAME")
async def role(ctx):
    """Say hello to the author"""  # the command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")


# Guild Slash Command Example with Any Specified Role Permissions
@bot.slash_command(guild_ids=[GUILD_ID], default_permission=False)
@permissions.has_any_role("ROLE_NAME", "ROLE_NAME2")
async def multirole(ctx):
    """Say hello to the author"""  # the command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")


# Guild Slash Command Example with Permission Decorator
@bot.slash_command(guild_ids=[GUILD_ID], default_permission=False)
@permissions.permission(user_id=USER_ID, permission=True)
async def permission_decorator(ctx):
    """Say hello to the author"""  # the command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")


# Guild Slash Command Example with Permissions Kwarg
@bot.slash_command(
    guild_ids=[GUILD_ID],
    default_permission=False,
    permissions=[permissions.Permission(id=USER_ID, type=2, permission=True)],
)
async def permission_kwarg(ctx):
    """Say hello to the author"""  # the command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")


# To learn how to add descriptions, choices to options check slash_options.py
bot.run("token")
