import discord

bot = discord.Bot()


@bot.user_command(guild_ids=[...])  # create a user command for the supplied guilds
async def mention(ctx, member: discord.Member):  # user commands return the member
    await ctx.respond(f"{ctx.author.name} just mentioned {member.mention}!")


# user commands and message commands can have spaces in their names
@bot.message_command(name="Show ID")  # creates a global message command
async def show_id(ctx, message: discord.Message):  # message commands return the message
    await ctx.respond(f"{ctx.author.name}, here's the message id: {message.id}!")


bot.run("TOKEN")
