import discord
from discord.app import Option


description = """An example to showcase how to extract info about users"""

bot = discord.Bot(commands_prefix="x", description="e",
                  intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@bot.slash_command(name="a", description="a")
async def perms(ctx, user: discord.Member):
    user = user or ctx.author
    e = discord.Embed()
    e.set_author(name=user.name)
    e.add_field(name='ID', value=user.id, inline=False)
    e.add_field(name='Joined', value=user.joined_at.strftime(
        "%A, %B %d %Y @ %H:%M:%S %p"), inline=False)
    e.add_field(name='Created', value=user.created_at.strftime(
        "%A, %B %d %Y @ %H:%M:%S %p"), inline=False)
    colour = user.colour
    if colour.value:

        e.colour = colour

    if isinstance(user, discord.User):
        e.set_footer(text='This member is not in this server.')

    await ctx.send(embed=e)

bot.run("token")
