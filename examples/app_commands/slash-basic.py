import discord

bot = discord.Bot()


@bot.command(guild_ids=[...])  # create a slash command for the supplied guilds
async def hello(ctx):
    """Say hello to the bot""" # the command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.user}!")


bot.run("TOKEN")
