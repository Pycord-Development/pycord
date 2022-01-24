"""
This init file will be called in bot.py before or after of cog import.
client: <discord.Bot> or <commands.Bot> should be present for the last method defined here 
for <client.add_application_command> method.

do note that the client.add_application_command should only be called in only one method and that method
should be called in the very last in the bot.py
"""

import discord
from discord.commands.commands import Option, SlashCommandGroup
from discord.ext.commands.context import Context

MathGroup = SlashCommandGroup("math", "maths!.", guild_ids=[...])


def addition():  # you can use whatever parameters needed for you command.
    # the main decorator will be called inside the method.
    @MathGroup.command(name="add", guild_ids=[...], description="addition!")
    async def add(
        ctx: Context,
        number1: Option(int, "first integer"),  # refer to slashOption.py
        number2: Option(int, "second integer"),  # refer to slashOption.py
    ):
        await ctx.respond(f"{number1}+{number2}={number1+number2}")


def subtraction(client):
    @MathGroup.command(name="subtract", guild_ids=[...], description="subtraction!")
    async def sub(
        ctx: Context,
        number1: Option(int, "first integer"),  # refer to slashOption.py
        number2: Option(int, "second integer"),  # refer to slashOption.py
    ):
        await ctx.respond(f"{number1}-{number2}={number1-number2}")

    client.add_application_command(MathGroup)
