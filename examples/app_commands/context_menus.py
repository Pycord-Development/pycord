# This example requires the 'members' privileged intent to use the Member converter,

import discord

intents = discord.Intents.default()
intents.members = True

bot = discord.Bot(debug_guilds=[...], intents=intents)


@bot.user_command()  # create a user command for the supplied guilds
async def mention(ctx: discord.ApplicationContext, member: discord.Member):  # user commands return the member
    await ctx.respond(f"{ctx.author.name} just mentioned {member.mention}!")


# user commands and message commands can have spaces in their names
@bot.message_command(name="Show ID")  # creates a global message command
async def show_id(ctx: discord.ApplicationContext, message: discord.Message):  # message commands return the message
    await ctx.respond(f"{ctx.author.name}, here's the message id: {message.id}!")


bot.run("TOKEN")
