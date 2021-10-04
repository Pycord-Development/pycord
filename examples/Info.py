import discord
from discord.ext import commands


# An example to showcase how to extract info about users

intents = discord.Intents(
            members=True,
            messages=True,
            )

bot = commands.Bot(command_prefix=".", description="e",
                  intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")



@bot.command()
async def userinfo(ctx, user: discord.Member):
    user = user or ctx.author
    e = discord.Embed()
    e.set_author(name=user.name)
    e.add_field(name='ID', value=user.id, inline=False)
    e.add_field(name='Joined', value=user.joined_at.strftime(
        "%A, %B %d %Y @ %H:%M:%S %p"), inline=False)
    e.add_field(name='Created', value=user.created_at.strftime(
        "%A, %B %d %Y @ %H:%M:%S %p"), inline=False)
    await ctx.send(embed=e, colour=user.colour)

bot.run("token")
