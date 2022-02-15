from discord import Intents
from discord.ext import commands, ipc

bot = commands.Bot(command_prefix="$", intents=Intents.all())
server = ipc.Server("localhost", "my_secret_token", bot)


@server.route()
async def get_member_count(data):
    guild = bot.get_guild(data.guild_id)  # get the guild.

    return guild.member_count  # send the member count.


server.run()
bot.run("token")
