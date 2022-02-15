import discord
from discord.ext import tasks


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # An attribute we can access from our task
        self.counter = 0

        # Start the task to run in the background
        self.my_background_task.start()

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    @tasks.loop(seconds=60)  # Task that runs every 60 seconds
    async def my_background_task(self):
        channel = self.get_channel(1234567)  # your Channel ID goes here
        self.counter += 1
        await channel.send(self.counter)

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # Wait until the bot logs in


client = MyClient()
client.run("token")
