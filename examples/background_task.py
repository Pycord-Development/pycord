from datetime import time, timezone

import discord
from discord.ext import tasks


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # An attribute we can access from our task
        self.counter = 0

        # Start the tasks to run in the background
        self.my_background_task.start()
        self.time_task.start()

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    @tasks.loop(seconds=60)  # Task that runs every 60 seconds
    async def my_background_task(self):
        channel = self.get_channel(1234567)  # Your Channel ID goes here
        self.counter += 1
        await channel.send(self.counter)

    @tasks.loop(
        time=time(3, 0, tzinfo=timezone.utc)  # Task that runs every day at 3 AM UTC
    )
    async def time_task(self):
        channel = self.get_channel(1234567)  # Your Channel ID goes here
        await channel.send("It's 3 AM!")

    @my_background_task.before_loop
    @time_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # Wait until the bot logs in


client = MyClient()
client.run("token")
