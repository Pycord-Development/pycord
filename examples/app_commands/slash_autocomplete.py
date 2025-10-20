from functools import partial

import discord
from discord.commands import option

bot = discord.Bot(debug_guilds=[...])

COLORS = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]

LOTS_OF_COLORS = [
    "aliceblue",
    "antiquewhite",
    "aqua",
    "aquamarine",
    "azure",
    "beige",
    "bisque",
    "blueviolet",
    "brown",
    "burlywood",
    "cadetblue",
    "cornflowerblue",
    "cornsilk",
    "crimson",
    "cyan",
    "darkblue",
    "deepskyblue",
    "dimgray",
    "dimgrey",
    "dodgerblue",
    "firebrick",
    "floralwhite",
    "forestgreen",
    "fuchsia",
    "gainsboro",
    "ghostwhite",
    "gold",
    "goldenrod",
    "gray",
    "green",
    "greenyellow",
    "grey",
    "honeydew",
    "hotpink",
    "indianred",
    "indigo",
    "ivory",
    "khaki",
    "lavender",
    "lavenderblush",
    "lawngreen",
    "lightcoral",
    "maroon",
    "mediumaquamarine",
    "mediumblue",
    "mediumorchid",
    "midnightblue",
    "navajowhite",
    "navy",
    "oldlace",
    "olive",
    "olivedrab",
    "orange",
    "orangered",
    "orchid",
    "palegoldenrod",
    "palegreen",
    "plum",
    "powderblue",
    "purple",
    "red",
    "rosybrown",
    "royalblue",
    "saddlebrown",
    "sienna",
    "springgreen",
    "steelblue",
    "tan",
    "teal",
    "thistle",
    "tomato",
    "turquoise",
    "violet",
    "wheat",
    "white",
    "whitesmoke",
    "yellow",
    "yellowgreen",
]

BASIC_ALLOWED = [
    ...
]  # This would normally be a list of discord user IDs for the purpose of this example


async def color_searcher(ctx: discord.AutocompleteContext):
    """
    Returns a list of matching colors from the LOTS_OF_COLORS list.

    In this example, we've added logic to only display any results in the
    returned list if the user's ID exists in the BASIC_ALLOWED list.

    This is to demonstrate passing a callback in the discord.utils.basic_autocomplete function.
    """

    return [
        color for color in LOTS_OF_COLORS if ctx.interaction.user.id in BASIC_ALLOWED
    ]


async def get_colors(ctx: discord.AutocompleteContext):
    """Returns a list of colors that begin with the characters entered so far."""
    return [color for color in COLORS if color.startswith(ctx.value.lower())]


async def get_animals(ctx: discord.AutocompleteContext):
    """Returns a list of animals that are (mostly) the color selected for the "color" option."""
    picked_color = ctx.options["color"]
    if picked_color == "red":
        return ["cardinal", "ladybug"]
    elif picked_color == "orange":
        return ["clownfish", "tiger"]
    elif picked_color == "yellow":
        return ["goldfinch", "banana slug"]
    elif picked_color == "green":
        return ["tree frog", "python"]
    elif picked_color == "blue":
        return ["blue jay", "blue whale"]
    elif picked_color == "indigo":
        return [
            "eastern indigo snake"
        ]  # Needs to return an iterable even if only one item
    elif picked_color == "violet":
        return ["purple emperor butterfly", "orchid dottyback"]
    else:
        return ["rainbowfish"]


@bot.slash_command(name="ac_example")
@option("color", description="Pick a color!", autocomplete=get_colors)
@option("animal", description="Pick an animal!", autocomplete=get_animals)
async def autocomplete_example(
    ctx: discord.ApplicationContext,
    color: str,
    animal: str,
):
    """
    Demonstrates using ctx.options to create options
    that are dependent on the values of other options.

    For the `color` option, a callback is passed, where additional
    logic can be added to determine which values are returned.

    For the `animal` option, the callback uses the input
    from the color option to return an iterable of animals
    """

    await ctx.respond(
        f"You picked {color} for the color, which allowed you to choose {animal} for"
        " the animal."
    )


@bot.slash_command(name="ac_basic_example")
@option(
    "color",
    description="Pick a color from this big list!",
    autocomplete=discord.utils.basic_autocomplete(color_searcher),
    # Demonstrates passing a callback to discord.utils.basic_autocomplete
)
@option(
    "animal",
    description="Pick an animal from this small list",
    autocomplete=discord.utils.basic_autocomplete(
        ["snail", "python", "cricket", "orca"]
    ),
    # Demonstrates passing a static iterable discord.utils.basic_autocomplete
)
async def autocomplete_basic_example(
    ctx: discord.ApplicationContext,
    color: str,
    animal: str,
):
    """
    This demonstrates using the discord.utils.basic_autocomplete helper function.

    For the `color` option, a callback is passed, where additional
    logic can be added to determine which values are returned.

    For the `animal` option, a static iterable is passed.

    While a small amount of values for `animal` are used in this example,
    iterables of any length can be passed to discord.utils.basic_autocomplete

    Note that the basic_autocomplete function itself will still only return a maximum of 25 items.
    """

    await ctx.respond(f"You picked {color} as your color, and {animal} as your animal!")


FRUITS = ["Apple", "Banana", "Orange"]
VEGETABLES = ["Carrot", "Lettuce", "Potato"]


async def food_autocomplete(
    ctx: discord.AutocompleteContext, food_type: str
) -> list[discord.OptionChoice]:
    items = FRUITS if food_type == "fruit" else VEGETABLES
    return [
        discord.OptionChoice(name=item)
        for item in items
        if ctx.value.lower() in item.lower()
    ]


@bot.slash_command(name="fruit")
@option(
    "choice",
    description="Pick a fruit",
    autocomplete=partial(food_autocomplete, food_type="fruit"),
)
async def get_fruit(ctx: discord.ApplicationContext, choice: str):
    await ctx.respond(f'You picked "{choice}"')


@bot.slash_command(name="vegetable")
@option(
    "choice",
    description="Pick a vegetable",
    autocomplete=partial(food_autocomplete, food_type="vegetable"),
)
async def get_vegetable(ctx: discord.ApplicationContext, choice: str):
    await ctx.respond(f'You picked "{choice}"')


bot.run("TOKEN")
