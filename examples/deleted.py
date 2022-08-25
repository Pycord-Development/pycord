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
    if message.content.startswith("!deleteme"):
        msg = await message.channel.send("I will delete myself now...")
        await msg.delete()

        # This also works:
        await message.channel.send("Goodbye in 3 seconds...", delete_after=3.0)


@bot.event
async def on_message_delete(message: discord.Message):
    msg = f"{message.author} has deleted the message: {message.content}"
    await message.channel.send(msg)


bot.run("TOKEN")

