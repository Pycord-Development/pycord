# If you want a more intuitive way of using message components, check
# out the other examples in this directory
import asyncio
import discord
from discord.ext import commands
from discord import ui

class ButtonBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("$"))
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")
        
bot = ButtonBot()

@bot.command(name="button", description="Wait for button press example from pycord")
async def button(ctx):
    """Waits for a button press"""
    
    button = ui.Button(style=discord.ButtonStyle.primary, label="Click me!")
    view = ui.View()
    view.add_item(button)
    await ctx.respond("Wait for button press example", view=view)
    message = await ctx.interaction.original_message()
    # ctx.respond doesn't return the message sent so we can get it
    # ourselves
    # Check for whether the interaction is related to this button or not
    def check(interaction):
        return (
            interaction.is_component()
            and button.custom_id == interaction.data["custom_id"]
        )
        # custom_id is a unique identifier for every message component
    try:
        interaction = await bot.wait_for("interaction", check=check, timeout=30)
        # Wait for the user to press the button.
        await interaction.response.send_message("Button pressed!")
    # TimeoutError will be raised by wait_for if an interaction that passes
    # the check is not recieved within 30 seconds
    except asyncio.TimeoutError:
        await message.edit(content="You did not respond after 30 seconds...", view=None)
        
bot.run("token")
