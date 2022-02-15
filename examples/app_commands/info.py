import discord
from discord.ext import commands

# imports

intents = discord.Intents(
    guilds=True,
    members=True,
    messages=True,
)

bot = commands.Bot(
    command_prefix="/",
    description="An example to showcase how to extract info about users",
    intents=intents,
)


@bot.slash_command(name="userinfo", description="gets the info of a user")
async def info(ctx, user: discord.Member = None):
    user = user or ctx.author  # if no user is provided it'll use the the author of the message
    e = discord.Embed()
    e.set_author(name=user.name)
    e.add_field(name="ID", value=user.id, inline=False)  # user ID
    e.add_field(
        name="Joined",
        value=discord.utils.format_dt(round(user.joined_at.timestamp()), "F"),
        inline=False,
    )  # When the user joined the server
    e.add_field(
        name="Created",
        value=discord.utils.format_dt(round(user.created_at.timestamp()), "F"),
        inline=False,
    )  # When the user's account was created
    colour = user.colour
    if colour.value:  # if user has a role with a color
        e.colour = colour

    if isinstance(user, discord.User):  # checks if the user in the server
        e.set_footer(text="This member is not in this server.")

    await ctx.respond(embed=e)  # sends the embed


bot.run("your token")
