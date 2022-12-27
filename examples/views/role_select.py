import discord

# Role selects (dropdowns) are a new type of select menu/dropdown Discord has added to people can select guild/server roles from a dropdown

# Defines a simple View that allows the user to use the Select menu.
# Using the decorator automatically sets `select_type` to `discord.ComponentType.role_select`, which is what you need
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.role_select(
        placeholder="Select roles...", min_values=1, max_values=3
    )  # Users can select a maximum of 3 roles in the dropdown
    async def role_select_dropdown(self, select, interaction):
        await interaction.response.send_message(
            f"You selected the following roles:"
            + f", ".join(f"{role.mention}" for role in select.values)
        )


bot = discord.Bot(debug_guilds=[...])


@bot.slash_command()
async def role_select(ctx: discord.ApplicationContext):
    """Sends a message with our dropdown that contains a role select."""

    # Create the view containing our dropdown
    view = DropdownView()

    # Sending a message containing our View
    await ctx.respond("Select roles:", view=view)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


bot.run("TOKEN")
