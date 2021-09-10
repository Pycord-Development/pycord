import discord
from discord.app import Option

bot = discord.Bot()

# If you use commands.Bot, @bot.slash_command should be used for
# slash commands. You can use @bot.slash_command with discord.Bot as well


@bot.slash_command(guild_ids=[...])
async def hello(
    ctx,
    name: Option(str, "Enter your name"),
    gender: Option(str, "Choose your gender", choices=["Male", "Female", "Other"]),
    age: Option(int, "Enter your age", required=False, default=18),
):
    await ctx.send(f"Hello {name}")

bot.run('TOKEN')
