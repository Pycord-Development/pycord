import discord
from discord.commands import slash_command, Option
bot = discord.Bot()

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

BASIC_ALLOWED = [123, 444, 55782]  # this would be a list of discord user IDs


# Simple example of using logic in a basic_autocomplete callback. In this case, we're only returning any results if the user's ID exists in the BASIC_ALLOWED list
async def color_searcher(ctx: discord.AutocompleteContext):
    return [color for color in LOTS_OF_COLORS if ctx.interaction.user.id in BASIC_ALLOWED]


async def get_colors(ctx: discord.AutocompleteContext):
    return [color for color in COLORS if color.startswith(ctx.value.lower())]


async def get_animals(ctx: discord.AutocompleteContext):
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
        return ["eastern indigo snake"]  # needs to return an iterable even if only one item
    elif picked_color == "violet":
        return ["purple emperor butterfly", "orchid dottyback"]
    else:
        return ["rainbowfish"]


@slash_command(name="ac_example", guild_ids=[...])
async def autocomplete_example(
    ctx: discord.ApplicationContext,
    color: Option(str, "Pick a color!", autocomplete=get_colors),
    animal: Option(str, "Pick an animal!", autocomplete=get_animals),
):
    await ctx.respond(f"You picked {color} for the color, which allowed you to choose {animal} for the animal.")


@slash_command(name="ac_basic_example", guild_ids=[...])
async def autocomplete_basic_example(
    ctx: discord.ApplicationContext,
    color: Option(str, "Pick a color from this big list", autocomplete=discord.utils.basic_autocomplete(color_searcher)),
    animal: Option(str, "Pick an animal from this small list", autocomplete=discord.utils.basic_autocomplete(["snail", "python", "cricket", "orca"])),
):
    await ctx.respond(f"You picked {color} as your color, and {animal} as your animal!")

bot.run("TOKEN")
