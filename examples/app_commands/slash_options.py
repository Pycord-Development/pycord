from typing import Union

import discord
from discord import option
from discord.commands import Option

bot = discord.Bot()


# If you use commands.Bot, @bot.slash_command should be used for
# slash commands. You can use @bot.slash_command with discord.Bot as well


@bot.slash_command(guild_ids=[...])
@option("name", description="Enter your name")
@option("gender", description="Choose your gender", choices=["Male", "Female", "Other"])
@option(
    "age",
    description="Enter your age",
    min_value=1,
    max_value=99,
    default=18,
    # passing the default value makes an argument optional
    # you also can create optional argument using:
    # age: Option(int, "Enter your age") = 18
)
async def hello(
    ctx: discord.ApplicationContext,
    name: str,
    gender: str,
    age: str,
):
    await ctx.respond(f"Hello {name}! Your gender is {gender} and you are {age} years old.")


@bot.slash_command(guild_ids=[...])
@option(
    "channel",
    [discord.TextChannel, discord.VoiceChannel],
    # you can specify allowed channel types by passing a list of them like this
    description="Select a channel",
)
async def channel(
    ctx: discord.ApplicationContext,
    channel: Union[discord.TextChannel, discord.VoiceChannel],
):
    await ctx.respond(f"Hi! You selected {channel.mention} channel.")


@bot.slash_command(name="attach_file")
@option("attachment", discord.Attachment, description="A file to attach to the message", required=False)
async def say(
    ctx: discord.ApplicationContext,
    attachment: discord.Attachment,
):
    """This demonstrates how to attach a file with a slash command."""
    file = await attachment.to_file()
    await ctx.respond("Here's your file!", file=file)


bot.run("TOKEN")
