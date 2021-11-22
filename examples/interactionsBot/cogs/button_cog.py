import discord
from discord.ext import commands
from discord.ext.commands.context import Context

from discord.commands import slash_command

class ButtonView(discord.ui.View):
    def __init__(self, ctx:Context=None):
        # making None is important if you want the button work after restart!
        super().__init__(timeout=None)
        self.ctx = ctx 

    #custom_id is required and should be unique for <commands.Bot.add_view>
    # attribute emoji can be used to include emojis which can be default str emoji or str(<:emojiName:int(ID)>)
    @discord.ui.button(style=discord.ButtonStyle.blurple,custom_id="counter:firstButton")
    async def leftButton(self,button,interaction):
        await interaction.response.send_message(f"first button was pressed!")

    #custom_id is required and should be unique for <commands.Bot.add_view>
    # attribute emoji can be used to include emojis which can be default str emoji or str(<:emojiName:int(ID)>)
    @discord.ui.button(style=discord.ButtonStyle.blurple,custom_id="counter:secondButton")
    async def rightButton(self,button,interaction):
        await interaction.response.send_message(f"second button was pressed!")
        
    """
    timeout is used if there is a timeout on the button interaction with is 180 by default
    
    async def on_timeout(self):
            for child in self.children:
                child.disabled = True
            await interaction.edit_original_message(view=None)
    """

class ButtonExample(commands.Cog):
    def __init__(self,client):
        self.client = client

    @slash_command(guild_ids=[...],name="slash_command_name",description="command description!")
    async def CommandName(self,ctx):
        navigator = ButtonView(ctx) # button View <discord.ui.View>
        await ctx.respond("",view=navigator) 

    @CommandName.error
    async def CommandName_error(self, ctx:Context ,error):
        return await ctx.respond(error,ephemeral=True) # ephemeral makes "Only you can see this" message

def setup(client):
    client.add_cog(ButtonExample(client))