import discord

bot = discord.Bot()


@bot.command(guild_ids=[...])  # create a slash command for the supplied guilds
async def hello(ctx):
    """Say hello to the bot""" # the command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")

@bot.command(name='global')  # creates a global slash command (might take an hour to register)
async def global_command(ctx, num: int): # Takes one integer parameter 
    await ctx.respond(f"This is a global command, {num}!")

bot.run("TOKEN")
