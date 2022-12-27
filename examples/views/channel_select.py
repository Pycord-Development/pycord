import discord

# Channel selects (dropdowns) are a new type of select menu/dropdown Discord has added to people can select channels from a dropdown

# Defines a simple View that allows the user to use the Select menu.
# In the view, we define the channel_select with `discord.ui.channel_select`
# Using the decorator automatically sets `select_type` to `discord.ComponentType.channel_select`, which is what you need
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.channel_select(
        placeholder="Select channels...", min_values=1, max_values=3
    )  # Users can select a maximum of 3 channels in the dropdown
    async def channel_select_dropdown(self, select, interaction):
        await interaction.response.send_message(
            f"You selected the following channels:"
            + f", ".join(f"{channel.mention}" for channel in select.values)
        )


bot = discord.Bot(debug_guilds=[...])


@bot.slash_command()
async def channel_select(ctx: discord.ApplicationContext):
    """Sends a message with our dropdown that contains a channel select."""

    # Create the view containing our dropdown
    view = DropdownView()

    # Sending a message containing our View
    await ctx.respond("Select channels:", view=view)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


bot.run("TOKEN")
