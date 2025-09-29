import asyncio
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
        await channel.send(str(self.counter))

    @tasks.loop(
        time=time(3, 0, tzinfo=timezone.utc)
    )  # Task that runs every day at 3 AM UTC
    async def time_task(self):
        channel = self.get_channel(1234567)  # Your Channel ID goes here
        await channel.send("It's 3 AM!")

    @my_background_task.before_loop
    @time_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # Wait until the bot logs in

    # Schedule every 10s; each run takes ~15s. With overlap=2, at most 2 runs
    # execute concurrently so we don't build an ever-growing backlog.
    @tasks.loop(seconds=10, overlap=2)
    async def fetch_status_task(self):
        """
        Practical overlap use-case:

        Poll an external service and post a short summary. Each poll may take
        ~15s due to network latency or rate limits, but we want fresh data
        every 10s. Allowing a small amount of overlap avoids drifting schedules
        without opening the floodgates to unlimited concurrency.
        """
        # Book-keeping so we can show concurrency in logs/messages
        run_no = self.fetch_status_task.current_loop

        try:
            print(f"[status] start run #{run_no}")

            # Simulate slow I/O (e.g., HTTP requests, DB queries, file I/O)
            await asyncio.sleep(15)

            channel = self.get_channel(1234567)  # Replace with your channel ID
            msg = f"[status] run #{run_no} complete"
            if channel:
                await channel.send(msg)
            else:
                print(msg)
        finally:
            print(f"[status] end run #{run_no}")


client = MyClient()
client.run("TOKEN")
