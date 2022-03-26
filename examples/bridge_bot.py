# This example requires the "message_content" privileged intent for the bridge command to work.

import discord
from discord.ext import bridge

intents = discord.Intents.default()
intents.message_content = True
bot = bridge.Bot(command_prefix="!", intents=intents)

@bot.bridge_command()
async def hello(ctx):
    await ctx.respond("Hello!")

@bot.bridge_command(name="getmemberid")
async def get_member_id(ctx, *, member: discord.Member):
    await ctx.respond(f"The member's ID is {member.id}")

bot.run("TOKEN")
