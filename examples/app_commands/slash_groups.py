import discord

bot = discord.Bot()

# If you use commands.Bot, @bot.slash_command should be used for
# slash commands. You can use @bot.slash_command with discord.Bot as well

math = bot.create_group(
    "math", "Commands related to mathematics."
)  # create a slash command group


@math.command(guild_ids=[...])  # create a slash command
async def add(ctx, num1: int, num2: int):
    """Get the sum of 2 integers."""
    await ctx.respond(f"The sum of these numbers is **{num1+num2}**")


# another way, creating the class manually

from discord.commands import SlashCommandGroup

math = SlashCommandGroup("math", "Commands related to mathematics.")


@math.command(guild_ids=[...])
async def add(ctx, num1: int, num2: int):
    ...


bot.add_application_command(math)

bot.run("TOKEN")
