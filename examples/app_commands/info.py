# Imports
import discord
from discord.ext import commands

intents = discord.Intents(
    guilds=True,
    members=True,
    messages=True,
)

bot = discord.Bot(intents=intents)

@bot.command(name="userinfo", description="Gets information about an user.", guild_ids=[...])
async def userinfo(ctx, *, user: discord.Member = None):
    # If the user is not provided, it will default to the message author.
    user = user or ctx.author

    embed = discord.Embed(
        title=f"User Info of {user}"
    )
    embed.set_author(name=user.name)
    embed.add_field(name="ID", value=user.id, inline=False) # ID of the user.
    embed.add_field(
        name="Joined",
        value=discord.utils.format_dt(round(user.joined_at.timestamp()), "F"),
        inline=False,
    )  # The timestamp of when the user joined the server.
    embed.add_field(
        name="Created",
        value=discord.utils.format_dt(round(user.created_at.timestamp()), "F"),
        inline=False,
    )  # The timestamp of the user creating their account.
    colour = user.colour
    if colour.value:  # if user has a role with a color
        embed.colour = colour

    if isinstance(user, discord.User):  # checks if the user in the server
        embed.set_footer(text="This member is not in this server.")

    await ctx.respond(embed=embed)  # Sends the embed


bot.run("your token")
