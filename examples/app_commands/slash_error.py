import discord

bot = discord.Bot()

# note - You can use this in a cog using @commands.Cog.listiner(), but it will only see application errors also in that cog, unlike on_command_error

# for more permissions, check slash_perms.py
@bot.slash_command(guild_ids=[...])  # create a slash command that requires ban_members permission
@bot.has_permissions(ban_members = True) # command decorator for user permissions
async def hello(ctx):
    """Say hello to the bot"""  
    await ctx.respond(f"Hello {ctx.author}!")


@bot.event # the event that runs when you dont have the ban members permission and run the `hello` command
async def on_application_command_error(ctx, error): # the `error` argument shows the error that happened
    await ctx.send(error) # Send the error to the user
    return # Return so that it doesn't clog up our terminal

# To learn how to add more and use commands, check slash_basic.py
bot.run("TOKEN")