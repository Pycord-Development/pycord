import discord
from discord.ext import commands
from typing import Union


description = """An example to showcase how to extract info about users"""

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="?", description=description, intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@bot.command()
async def info(ctx, *, user: Union[discord.Member, discord.User] = None):
    """Shows info about a user."""

    user = user or ctx.author
    e = discord.Embed()
    roles = [role.name.replace('@', '@\u200b') for role in getattr(user, 'roles', [])]
    e.set_author(name=str(user))



    e.add_field(name='ID', value=user.id, inline=False)
    e.add_field(name='Joined', value=round_time(user.joined_at), inline=False)
    e.add_field(name='Created', value=round_time(user.created_at), inline=False)

    voice = getattr(user, 'voice', None)
    if voice is not None:
        vc = voice.channel
        other_people = len(vc.members) - 1
        voice = f'{vc.name} with {other_people} others' if other_people else f'{vc.name} by themselves'
        e.add_field(name='Voice', value=voice, inline=False)

    if roles:
        e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles', inline=False)

    colour = user.colour
    if colour.value:
        e.colour = colour

    if user.avatar:
        e.set_thumbnail(url=user.display_avatar.url)

    if isinstance(user, discord.User):
        e.set_footer(text='This member is not in this server.')

    await ctx.send(embed=e)

bot.run("token")
