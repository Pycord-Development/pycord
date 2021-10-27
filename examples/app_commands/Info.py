import discord
from discord.ext import commands

intents = discord.Intents(
            guilds=True,
            members=True,
            messages=True,
            )
bot = commands.Bot(command_prefix=".", description="An example to showcase how to extract info about users",intents=intents)



@bot.slash_command(name="userinfo", description="gets the info of a user")
async def info(ctx, user: discord.Member = None):
    user = user or ctx.author
    e = discord.Embed()
    e.set_author(name=user.name)
    e.add_field(name='ID', value=user.id, inline=False)
    e.add_field(name='Joined',
                value=f"<t:{round(user.joined_at.timestamp())}:F>", inline=False)
    e.add_field(name='Created',
                value=f"<t:{round(user.created_at.timestamp())}:F>", inline=False)
    colour = user.colour
    if colour.value:

        e.colour = colour

    if isinstance(user, discord.User):
        e.set_footer(text='This member is not in this server.')

    await ctx.respond(embed=e)
    
    
bot.run("urtoken")


