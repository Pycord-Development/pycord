# This example requires the `message_content` privileged intent for prefixed commands.

import random

import discord
from discord.ext import commands


class MyContext(commands.Context):  # Custom context
    async def tick(self, value: bool):
        # Reacts to the message with an emoji
        # depending on whether value is True or False.
        # If it's True, it'll add a green check mark.
        # Otherwise, it'll add a red cross mark.
        emoji = "\N{WHITE HEAVY CHECK MARK}" if value else "\N{CROSS MARK}"
        try:
            # This will react to the command author's message.
            await self.message.add_reaction(emoji)
        except discord.HTTPException:
            # Sometimes errors occur during this, for example,
            # maybe you don't have permission to add reactions.
            # We don't mind, so we can just ignore them.
            pass


# You can subclass discord.ApplicationContext to create custom application context if needed
class MyApplicationContext(discord.ApplicationContext):  # Custom application context
    async def success(self, message: str):
        try:  # Respond with a green embed with a title of "Success"
            embed = discord.Embed(title="Success", description=message, colour=discord.Colour.green())
            await self.respond(embeds=[embed])
        except discord.HTTPException:  # Ignore exceptions
            pass


class MyBot(commands.Bot):
    async def get_context(self, message: discord.Message, *, cls=MyContext):
        # When you override this method, you pass your new Context
        # subclass to the super() method, which tells the bot to
        # use the new MyContext class.
        return await super().get_context(message, cls=cls)

    async def get_application_context(self, interaction: discord.Interaction, cls=MyApplicationContext):
        # The same method for custom application context.
        return await super().get_application_context(interaction, cls=cls)


intents = discord.Intents.default()
intents.message_content = True

bot = MyBot(command_prefix=commands.when_mentioned_or("!"), debug_guilds=[...], intents=intents)


@bot.command()
async def guess(ctx: MyContext, number: int):
    """Guess a random number from 1 to 6."""
    # Explained in a previous example, this
    # gives you a random number from 1-6.
    value = random.randint(1, 6)
    # With your new helper function, you can add a
    # green check mark if the guess was correct,
    # or a red cross mark if it wasn't.
    await ctx.tick(number == value)


@bot.slash_command()
async def slash_guess(ctx: MyApplicationContext, number: int):
    """Guess a random number from 1 to 6."""
    value = random.randint(1, 6)
    if number == value:
        await ctx.success("Congratulations! You guessed the number.")  # Use the new helper function
    else:
        await ctx.respond("You are wrong! Try again.")


# IMPORTANT: You shouldn't hard code your token
# These are very important, and leaking them can
# let people do very malicious things with your
# bot. Try to use a file or something to keep
# them private, and don't commit it to GitHub.
bot.run("TOKEN")
