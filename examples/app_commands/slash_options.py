import discord
from discord.commands import Option


bot = discord.Bot()
# If you use commands.Bot, @bot.slash_command should be used for
# slash commands. You can use @bot.slash_command with discord.Bot as well


@bot.slash_command(guild_ids=[...])
async def hello(
    ctx: discord.ApplicationContext,
    name: Option(str, "Enter your name"),
    gender: Option(str, "Choose your gender", choices=["Male", "Female", "Other"]),
    age: Option(int, "Enter your age", min_value=1, max_value=99, default=18)
    # passing the default value makes an argument optional
    # you also can create optional argument using:
    # age: Option(int, "Enter your age") = 18
):
    await ctx.respond(f"Hello {name}! Your gender is {gender} and you are {age} years old.")


@bot.slash_command(guild_ids=[...])
async def channel(
    ctx: discord.ApplicationContext,
    channel: Option([discord.TextChannel, discord.VoiceChannel], "Select a channel")
    # you can specify allowed channel types by passing a list of them like: [discord.TextChannel, discord.VoiceChannel]
):
    await ctx.respond(f"Hi! You selected {channel.mention} channel.")



bot.run("TOKEN")
