import discord

intents = discord.Intents.default()
intents.message_content = True  # < This may give you `read-only` warning, just ignore it.
# This intent requires "Message Content Intent" to be enabled at https://discord.com/developers


bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print('Ready!')


@bot.event
async def on_message(message: discord.Message):
    # Make sure we won't be replying to ourselves.
    if message.author.id == bot.user.id:
        return

    if message.content.startswith("!hello"):
        await message.reply("Hello!", mention_author=True)


bot.run("TOKEN")
