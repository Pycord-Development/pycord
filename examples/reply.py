import discord


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_message(self, message):
        # ensures that the bot does not reply to itself
        if message.author.id != self.user.id and message.content.startswith("!hello"):
            await message.reply("Hello!", mention_author=True)


client = MyClient()
client.run("token")
