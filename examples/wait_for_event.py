# This example requires the `message_content` privileged intent for access to message content.

import asyncio
import random

import discord


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_message(self, message: discord.Message):
        # Make sure we won't be replying to ourselves.
        if message.author.id == self.user.id:
            return

        if message.content.startswith("$guess"):
            await message.channel.send("Guess a number between 1 and 10.")

            def is_valid_guess(m: discord.Message):
                return m.author == message.author and m.content.isdigit()

            answer = random.randint(1, 10)

            try:
                guess = await self.wait_for("message", check=is_valid_guess, timeout=5.0)
            except asyncio.TimeoutError:
                return await message.channel.send(f"Sorry, you took too long it was {answer}.")

            if int(guess.content) == answer:
                await message.channel.send("You are right!")
            else:
                await message.channel.send(f"Oops. It is actually {answer}.")


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run("TOKEN")
