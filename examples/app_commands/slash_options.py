import discord
from discord.app import Option
# if you get a import error, make sure you installed
# pip install git+https://github.com/Pycord-Development/pycord@slash

bot = discord.Bot()

# If you use commands.Bot, @bot.slash_command should be used for
# slash commands. You can use @bot.slash_command with discord.Bot aswell


@bot.command(guild_ids=[...])
async def hello(
    ctx,
    name: Option(str, "Enter your name"),
    gender: Option(str, "Choose your gender", choices=["Male", "Female", "Other"]),
    age: Option(int, "Enter your age", required=False, default=18),
):
    await ctx.send(f"Hello {name}")
    
@bot.slash_command(name="wish", description="Wish another member") # This will become a global slash command. However, global slash commands can take up to 1 hour to register.
@commands.has_role("myRole") # make sure you have updated to the latest version of the slash branch.
async def wish(
    ctx,
    member: Option(discord.Member, "The Member you want to wish")
):
    await ctx.send(f"{ctx.author.mention} wishes {member}!")
