# This example requires the `message_content` privileged intent for access to message content.

import asyncio

import discord


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_message(self, message: discord.Message):
        if message.content.startswith("!editme"):
            msg = await message.channel.send("10")
            await asyncio.sleep(3.0)
            await msg.edit(content="40")

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        msg = f"**{before.author}** edited their message:\n{before.content} -> {after.content}"
        await before.channel.send(msg)


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run("TOKEN")
