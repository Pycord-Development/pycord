import random

import discord
from discord.ext import commands


class MyContext(commands.Context):  # custom context
    async def tick(self, value):
        # reacts to the message with an emoji
        # depending on whether value is True or False
        # if its True, it'll add a green check mark
        # otherwise, it'll add a red cross mark
        emoji = "\N{WHITE HEAVY CHECK MARK}" if value else "\N{CROSS MARK}"
        try:
            # this will react to the command author's message
            await self.message.add_reaction(emoji)
        except discord.HTTPException:
            # sometimes errors occur during this, for example
            # maybe you don't have permission to do that
            # we don't mind, so we can just ignore them
            pass


# you can subclass discord.ApplicationContext to create custom application context if needed
class MyApplicationContext(discord.ApplicationContext):  # custom application context
    async def success(self, message):
        try:
            await self.respond(embed=discord.Embed(  # respond with a green embed with "Success" title
                title="Success",
                description=message,
                colour=discord.Colour.green()
            ))
        except discord.HTTPException:  # ignore exceptions
            pass


class MyBot(commands.Bot):
    async def get_context(self, message, *, cls=MyContext):
        # when you override this method, you pass your new Context
        # subclass to the super() method, which tells the bot to
        # use the new MyContext class
        return await super().get_context(message, cls=cls)

    async def get_application_context(self, interaction, cls=MyApplicationContext):
        # the same stuff for custom application context
        return await super().get_application_context(interaction, cls=cls)


bot = MyBot(command_prefix="!")


@bot.command()
async def guess(ctx, number: int):
    """Guess a random number from 1 to 6."""
    # explained in a previous example, this gives you
    # a random number from 1-6
    value = random.randint(1, 6)
    # with your new helper function, you can add a
    # green check mark if the guess was correct,
    # or a red cross mark if it wasn't
    await ctx.tick(number == value)


@bot.slash_command(guild_ids=[...])
async def slash_guess(ctx, number: int):
    """Guess a random number from 1 to 6."""
    value = random.randint(1, 6)
    if number == value:
        await ctx.success("Congratulations! You guessed the number.")  # use the new helper function
    else:
        await ctx.respond("You are wrong! Try again.")


# IMPORTANT: You shouldn't hard code your token
# these are very important, and leaking them can
# let people do very malicious things with your
# bot. Try to use a file or something to keep
# them private, and don't commit it to GitHub
bot.run("TOKEN")
