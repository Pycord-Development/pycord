# This example requires the `message_content` privileged intent for access to message content.

import discord


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_message(self, message: discord.Message):
        if message.content.startswith("!deleteme"):
            msg = await message.channel.send("I will delete myself now...")
            await msg.delete()

            # This also works:
            await message.channel.send("Goodbye in 3 seconds...", delete_after=3.0)

    async def on_message_delete(self, message: discord.Message):
        msg = f"{message.author} has deleted the message: {message.content}"
        await message.channel.send(msg)


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run("TOKEN")
