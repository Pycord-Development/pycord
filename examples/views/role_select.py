import discord

# Role selects (dropdowns) are a new type of select menu/dropdown Discord has added so people can select server roles from a dropdown.


# Defines a simple View that allows the user to use the Select menu.
# In this view, we define the role_select with `discord.ui.role_select`
# Using the decorator automatically sets `select_type` to `discord.ComponentType.role_select`.
class DropdownView(discord.ui.View):
    @discord.ui.role_select(
        placeholder="Select roles...", min_values=1, max_values=3
    )  # Users can select a maximum of 3 roles in the dropdown
    async def role_select_dropdown(
        self, select: discord.ui.RoleSelect, interaction: discord.Interaction
    ) -> None:
        # update the select default values to set them to the select ones
        select.default_values = select.values  # this is a list of Role
        await interaction.response.send_message(
            "You selected the following roles:"
            + ", ".join(f"{role.mention}" for role in select.values),
            view=self,
        )


bot: discord.Bot = discord.Bot(debug_guilds=[...])


@bot.slash_command()
async def role_select(ctx: discord.ApplicationContext) -> None:
    """Sends a message with our dropdown that contains a role select."""

    # Create the view containing our dropdown
    view = DropdownView()

    # Sending a message containing our View
    await ctx.respond("Select roles:", view=view)


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


bot.run("TOKEN")
