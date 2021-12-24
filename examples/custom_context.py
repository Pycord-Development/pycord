import random

import discord
from discord.ext import commands


class MyContext(commands.Context):
    async def tick(self, value):
        # Reacts to the message with an emoji
        # Depending on whether value is True or False
        # If its True, it'll add a green check mark
        # Otherwise, it'll add a red cross mark
        emoji = "\N{WHITE HEAVY CHECK MARK}" if value else "\N{CROSS MARK}"
        try:
            # This will react to the command author's message
            await self.message.add_reaction(emoji)
        except discord.HTTPException:
            # Sometimes errors occur during this, for example
            # Maybe you don't have permission to do that
            # We don't mind, so we can just ignore them
            pass


class MyBot(commands.Bot):
    async def get_context(self, message, *, cls=MyContext):
        # When you override this method, you pass your new Context
        # Subclass to the super() method, which tells the bot to
        # Use the new MyContext class
        return await super().get_context(message, cls=cls)


bot = MyBot(command_prefix="!")


@bot.command()
async def guess(ctx, number: int):
    """Guess a random number from 1 to 6."""
    # explained in a previous example, this gives you
    # a random number from 1-6
    value = random.randint(1, 6)
    # With your new helper function, you can add a
    # Green check mark if the guess was correct,
    # Or a red cross mark if it wasn't
    await ctx.tick(number == value)


# IMPORTANT: You shouldn't hard code your token
# These are very important, and leaking them can
# let people do very malicious things with your
# bot. Try to use a file or something to keep
# Them private, and don't commit it to GitHub
token = "your token here"
bot.run(token)
