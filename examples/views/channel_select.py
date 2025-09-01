import discord

# Channel selects (dropdowns) are a new type of select menu/dropdown Discord has added so users can select channels from a dropdown.


# Defines a simple View that allows the user to use the Select menu.
# In this view, we define the channel_select with `discord.ui.channel_select`
# Using the decorator automatically sets `select_type` to `discord.ComponentType.channel_select`.
class DropdownView(discord.ui.View):
    @discord.ui.channel_select(
        placeholder="Select channels...", min_values=1, max_values=3
    )  # Users can select a maximum of 3 channels in the dropdown
    async def channel_select_dropdown(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ) -> None:
        # update the select default values to the chosen values
        select.default_values = select.values  # this is a list of GuildChannels
        await interaction.response.send_message(
            "You selected the following channels:"
            + ", ".join(f"{channel.mention}" for channel in select.values)
        )


bot: discord.Bot = discord.Bot(debug_guilds=[...])


@bot.slash_command()
async def channel_select(ctx: discord.ApplicationContext) -> None:
    """Sends a message with our dropdown that contains a channel select."""

    # Create the view containing our dropdown
    view = DropdownView()

    # Sending a message containing our View
    await ctx.respond("Select channels:", view=view)


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


bot.run("TOKEN")
