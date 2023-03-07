import discord
import asyncio

intents = discord.Intents.default()
intents.members = (True
                  # If you get the read_only warning ignore it
)
# You need to activate the "SERVER MEMBERS INTENT" at https://discord.com/developers
# to use the "playing with AMOUNT members in line 25

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print("Ready")
    bot.loop.create_task(status_task())


async def status_task():
    while True:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"PyCord Docs"))
        await asyncio.sleep(300)
        await bot.change_presence(activity=discord.Game(name=f"with {len(bot.users)} members"))
        await asyncio.sleep(300)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="https://pycord.dev/"))
        await asyncio.sleep(300)

bot.run("TOKEN")
