# This example requires the 'members' privileged intent to use the Member converter.

import discord

intents = discord.Intents.default()
intents.members = True

bot = discord.Bot(debug_guilds=[...], intents=intents)
# Remove debug_guilds and set guild_ids in the slash command decorators
# to restrict specific commands to the supplied guild IDs.


@bot.user_command()  # Create a global user command
async def mention(ctx: discord.ApplicationContext, member: discord.Member):  # User commands give a member param
    await ctx.respond(f"{ctx.author.name} just mentioned {member.mention}!")


# User commands and message commands can have spaces in their names
@bot.message_command(name="Show ID")  # Creates a global message command
async def show_id(ctx: discord.ApplicationContext, message: discord.Message):  # Message commands give a message param
    await ctx.respond(f"{ctx.author.name}, here's the message id: {message.id}!")


bot.run("TOKEN")
