import asyncio

import discord


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def my_background_task(self):
        await self.wait_until_ready()
        counter = 0
        channel = self.get_channel(1234567)  # Your channel ID goes here
        while not self.is_closed():
            counter += 1
            await channel.send(str(counter))
            await asyncio.sleep(60)  # This asyncio task runs every 60 seconds


client = MyClient()
client.run("TOKEN")
