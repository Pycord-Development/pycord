import random
import discord
from asyncio import TimeoutError

intents = discord.Intents.default()
intents.message_content = True  # < This may give you `read-only` warning, just ignore it.
# This intent requires "Message Content Intent" to be enabled at https://discord.com/developers


bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print('Ready!')


# For more examples regarding slash commands, checkout:
# https://github.com/Pycord-Development/pycord/tree/master/examples/app_commands

@bot.slash_command(name="guess", description="Guess a number between 1 and 10!")
async def guess_number(ctx: discord.ApplicationContext):
    await ctx.respond("Type in your number. *(It should be between 1 and 10)*")

    def is_valid_guess(m: discord.Message):
        # This function checks three things at once:
        # - The author of the message we've received via
        #   the wait_for is the same as command author.
        # - The content of the message is a digit.
        # - The digit received is within the range of 1-10.
        # If any one of these checks fail, we ignore this message.
        return m.author == ctx.author and m.content.isdigit() and 1 <= int(m.content) <= 10

    answer = random.randint(1, 10)

    try:
        guess: discord.Message = await bot.wait_for("message", check=is_valid_guess, timeout=5.0)
    except TimeoutError:
        return await ctx.send_followup(f"Sorry, you took too long it was {answer}.")

    if int(guess.content) == answer:
        await guess.reply("You are right!", mention_author=True)
    else:
        await guess.reply(f"Oops. It is actually {answer}.", mention_author=True)


bot.run("TOKEN")
