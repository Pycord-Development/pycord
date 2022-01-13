import discord
from discord.ext import commands

client = commands.Bot(command_prefix="+")
client.load_extension("jishaku")
"""
@client.slash_command()
async def testing(
    ctx,
    opt1: discord.commands.Option(int, "insert your favourite number"),
    opt2: discord.commands.Option(str, "insert your favourite string"),
    opt3: discord.commands.Option(discord.Member, "insert your favourite person")
):
    await ctx.respond(f"{opt1} + {opt2} = {opt3.mention}")
"""
client.run("ODgxMjE1OTc3NTE2MzMxMDI4.YSpmVQ.IRLFI25AIQsYNfvuc6aVz_S3bVo")
