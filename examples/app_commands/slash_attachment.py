import discord
from discord.commands import Option
from discord.enums import SlashCommandOptionType

bot = discord.Bot()


@bot.slash_command(name="attach_file")
async def say(
    ctx: discord.ApplicationContext,
    attachment: Option(
        SlashCommandOptionType.attachment,
        "File to attach to the message?",
        required=False,
    ),
):
    """This demonstrates how to attach a file with a slash command."""
    file = await attachment.to_file()
    await ctx.respond("Here's your file!", file=file)


bot.run("TOKEN")
