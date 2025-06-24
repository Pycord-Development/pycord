import discord
import os
from dotenv import load_dotenv

load_dotenv()

bot = discord.Bot()


@bot.slash_command()
async def hi(ctx: discord.ApplicationContext):
    """Test command to show user information."""
    await ctx.respond(f"Hello {ctx.author.name}!")


bot.run(os.getenv("TOKEN_2"))
