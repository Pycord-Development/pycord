"""
with slash commands user permission it's better to check with <ctx.author.guild_permissions> property
"""

import discord
from discord.ext import commands
import os
from cogs.button_cog import memeNavigator

#inherits commands.Bot
class BotClass(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=">")
        self.persistent_views_added = False
    
    # For making the intreaction Button works even after restart.
    async def on_ready(self):
        if not self.persistent_views_added:
            
            #adding memeNavigator class to the <commands.Bot.add_view> to make it work after restart
            self.add_view(memeNavigator())

            print(f'Connected as {self.user} with ID {self.user.id}')
            print("------")
            self.persistent_views_added = True
    
client = BotClass()

for filename in os.listdir('./cogs'):
    if filename.endswith(".py"):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run("token")
