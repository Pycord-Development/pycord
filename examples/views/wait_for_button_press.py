import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio

bot = commands.Bot(command_prefix="!")


GUILD_ID = ID

@bot.slash_command(name="test", guild_ids=[GUILD_ID])
async def test(ctx):
    await ctx.defer()
    embed = discord.Embed(description=f'Wait for button press example')
    embed.set_author(name=f'Pycord-Development')
    
    button = Button(style=discord.ButtonStyle.green, label="Click me!")

    view = View()

    view.add_item(button)

    msg = await ctx.send_followup(embed=embed, view=view)

    def check(interaction):
        return interaction.channel.id == ctx.channel.id and interaction.user.id == ctx.author.id

    try:
        interaction = await bot.wait_for('interaction', check=check, timeout=30)

        if f"{button.custom_id}" in str(interaction.data):
            await msg.reply("Button pressed!")
    

    except asyncio.TimeoutError:
        embed = discord.Embed(description=f'Wait for button press example failed (timeout)')
        embed.set_author(name=f'Pycord-Development')
        await msg.edit(embed=embed)




bot.run("TOKEN")
