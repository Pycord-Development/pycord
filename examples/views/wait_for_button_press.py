import asyncio
import discord
from discord.ui import Button, View


bot = discord.Bot()


@bot.slash_command(guild_ids=[...], description="Wait for button press example from pycord") 
async def button(ctx):
    ###############
    # Create button and add it to View()
    button = Button(style=discord.ButtonStyle.green, label="Click me!")
    view = View()
    view.add_item(button)
    ###############
    
    ###############
    # Create embed and send message with button and embed.
    embed = discord.Embed(description="Wait for button press example")
    embed.set_author(name="Pycord-Development")
    
    await ctx.respond(embed=embed, view=view)
    msg = await ctx.interaction.original_message()
    ###############
    
    ###############
    # Check whether the user who pressed the button is the ctx.author and the channel
    def check(interaction):
        return interaction.channel.id == ctx.channel.id and interaction.user.id == ctx.author.id
    ###############
    try:
        interaction = await bot.wait_for('interaction', check=check, timeout=30)
        # Wait for the user to press the button.

        if button.custom_id == interaction.data["custom_id"]:
            # Checks whether the custom_id of the button we specified above is the same as the one the user pressed.
            await interaction.response("Button pressed!")

    # Executes if they button is not pressed after a certain time...
    except asyncio.TimeoutError:
        embed = discord.Embed(description="Wait for button press example failed (timeout)")
        embed.set_author(name="Pycord-Development")
        await msg.edit(embed=embed)



bot.run("TOKEN")
