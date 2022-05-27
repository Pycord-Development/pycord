# This example requires the `message_content` privileged intent for access to message content.

import discord


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_message(self, message: discord.Message):
        # Make sure we won't be replying to ourselves.
        if message.author.id == self.user.id:
            return

        if message.content.startswith("!hello"):
            await message.reply("Hello!", mention_author=True)


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run("TOKEN")
