from functools import partial
from os import getenv

from dotenv import load_dotenv

import discord
from discord.ext import commands

load_dotenv()

bot = discord.Bot()

fruits = ["Apple", "Banana", "Orange"]
vegetables = ["Carrot", "Lettuce", "Potato"]


async def food_autocomplete(
    ctx: discord.AutocompleteContext, food_type: str
) -> list[discord.OptionChoice]:
    items = fruits if food_type == "fruit" else vegetables
    return [
        discord.OptionChoice(name=item)
        for item in items
        if ctx.value.lower() in item.lower()
    ]


class FoodCog(commands.Cog):
    @commands.slash_command(name="fruit")
    @discord.option(
        "choice",
        "Pick a fruit",
        autocomplete=partial(food_autocomplete, food_type="fruit"),
    )
    async def get_fruit(self, ctx: discord.ApplicationContext, choice: str):
        await ctx.respond(f'You picked "{choice}"')

    @commands.slash_command(name="vegetable")
    @discord.option(
        "choice",
        "Pick a vegetable",
        autocomplete=partial(food_autocomplete, food_type="vegetable"),
    )
    async def get_vegetable(self, ctx: discord.ApplicationContext, choice: str):
        await ctx.respond(f'You picked "{choice}"')


bot.add_cog(FoodCog())
bot.run(getenv("TOKEN"))
