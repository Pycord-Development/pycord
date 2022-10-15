import discord

bot = discord.Bot(debug_guilds=[...])

# If you use commands.Bot, @bot.slash_command should be used for
# slash commands. You can use @bot.slash_command with discord.Bot as well.

math = bot.create_group(
    "math", "Commands related to mathematics."
)  # Create a slash command group

# Another way, creating the class manually:

math = discord.SlashCommandGroup("math", "Commands related to mathematics.")


@math.command()  # Create a slash command under the math group
async def add(ctx: discord.ApplicationContext, num1: int, num2: int):
    """Get the sum of 2 integers."""
    await ctx.respond(f"The sum of these numbers is **{num1+num2}**")


bot.add_application_command(math)
bot.run("TOKEN")
