import discord

bot = discord.Bot()


# Note: If you want you can use commands.Bot instead of discord.Bot
# Use discord.Bot if you don't want prefixed message commands

# With discord.Bot you can use @bot.command as an alias
# of @bot.slash_command but this is overridden by commands.Bot


@bot.slash_command(guild_ids=[...])  # create a slash command for the supplied guilds
async def hello(ctx):
    """Say hello to the bot"""  # the command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")
    # Please note that you MUST respond with ctx.respond(), ctx.defer(), or any other
    # interaction response within 3 seconds in your slash command code, otherwise the
    # interaction will fail.


@bot.slash_command(
    name="hi"
)  # Not passing in guild_ids creates a global slash command (might take an hour to register)
async def global_command(ctx, num: int):  # Takes one integer parameter
    await ctx.respond(f"This is a global command, {num}!")


@bot.slash_command(guild_ids=[...])
async def joined(ctx, member: discord.Member = None):  # Passing a default value makes the argument optional
    user = member or ctx.author
    await ctx.respond(f"{user.name} joined at {discord.utils.format_dt(user.joined_at)}")


# To learn how to add descriptions and choices to options, check slash_options.py
bot.run("TOKEN")
