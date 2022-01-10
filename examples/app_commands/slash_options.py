import discord
from discord.commands import Option

bot = discord.Bot()

# If you use commands.Bot, @bot.slash_command should be used for
# slash commands. You can use @bot.slash_command with discord.Bot as well


@bot.slash_command(guild_ids=[...])
async def hello(
    ctx,
    name: Option(str, name="your_name", description="Enter your name"),
    gender: Option(str, description="Choose your gender", choices=["Male", "Female", "Other"]),
    age: Option(int, description="Enter your age", default=18)  # passing default value makes an argument optional
    # you also can specify default value using age: Option(int, description="Enter your age") = 18
):
    await ctx.respond(f"Hello {name}")


@bot.slash_command(guild_ids=[...])
async def channel(
    ctx,
    channel: Option([discord.TextChannel, discord.VoiceChannel], description="Select a channel")
    # you can specify channel types providing a list of them like [discord.TextChannel, discord.VoiceChannel]
):
    await ctx.respond(f"You selected {channel.mention} channel")


bot.run("TOKEN")
