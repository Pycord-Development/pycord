"""
with slash commands user permission it's better to check with <ctx.author.guild_permissions> property
"""

import os
import re

import discord
from discord.ui.view import View

PY_FILE_REGEX = re.compile(r"(?P<filename>[a-zA-Z0-9_-.,]+)\.py")

# inherits discord.Bot
class BotClass(discord.Bot):
    def __init__(self):
        super().__init__()
        self.persistent_views_added = False

    # For making the intreaction Button works even after restart.
    async def on_ready(self):
        if not self.persistent_views_added:

            # You can add <discord.ui.View> classes to the <commands.Bot.add_view> to make it work after restart
            # self.add_view(<discord.ui.View>)

            print(f"Connected as {self.user} with ID {self.user.id}")
            print("------")
            self.persistent_views_added = True


bot = BotClass()

py_files = list(file.group(1) if PY_FILE_REGEX.match(file) for file in os.listdir("./cogs"))
for file in py_files:
    bot.load_extension(f"cogs.{file}")

# using SlashCommandGroup
import cog_group

cog_group.addition()
# subtraction method is called last because of <client.add_application_command> inside it.
# calling subtraction first then addition would most likely not work and won't register addition slash command.
cog_group.subtraction(bot)

bot.run("token")
