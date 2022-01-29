import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio

bot = commands.Bot(command_prefix="!")


@bot.slash_command(name="button", guild_ids=[...], description="Wait for button press example from py-cord") ## Create a slash command for the supplied guilds.
async def button(ctx):
    await ctx.defer()
    
    ###############
    # Create button and add it to View()
    button = Button(style=discord.ButtonStyle.green, label="Click me!")
    view = View()
    view.add_item(button)
    ###############
    
    ###############
    # Create embed and send message with button and embed.
    embed = discord.Embed(description=f'Wait for button press example')
    embed.set_author(name=f'Pycord-Development')
    
    msg = await ctx.send_followup(embed=embed, view=view)
    ###############
    
    ###############
    # Check if the user who pressed the button is the ctx.author and the channel
    def check(interaction):
        return interaction.channel.id == ctx.channel.id and interaction.user.id == ctx.author.id
    ###############

    
    try:
        interaction = await bot.wait_for('interaction', check=check, timeout=30)
        # Wait for the user to press the button.

        if f"{button.custom_id}" in str(interaction.data):
            # Checks if the custom_id of the button we specified above is the same as the one the user pressed.
            await msg.reply("Button pressed!")
    

    # If after a certain time the key is not pressed...
    except asyncio.TimeoutError:
        embed = discord.Embed(description=f'Wait for button press example failed (timeout)')
        embed.set_author(name=f'Pycord-Development')
        await msg.edit(embed=embed)
    





bot.run("TOKEN")
