import discord
import asyncio
import asyncinit


bot = discord.Bot()

# Identical to dynamic_user_dropdown.py but
# includes the ability to use an asynchronous function
# for your dynamic menu generating function
# You'll need asyncinit | pip install asyncinit==0.2.4

async def external_user_specific_list_function(discord_id):
    #Replace this example with whatever your source is
    #for the users dynamically generated items
    users_menu_items = []
    await asyncio.sleep(.1)
    for i in range(5):
        users_menu_items.append(f'Item #{i + 1}) - Dynamically Generated for <@{discord_id}>')
        i += 1
    return users_menu_items


@asyncinit
class Dropdown(discord.ui.Select):
    async def __init__(self, interaction):
        # In this example, we are passing in the interaction object from the calling interaction.
        self.value = None
        self.interaction = interaction
        self.discord_user = interaction.user.id
        self.users_menu_items = await external_user_specific_list_function(self.discord_user)
        options = [discord.SelectOption(label=menu_item) for menu_item in self.users_menu_items]
        #Label only in this example. But you could return a list of lists to populate other tags as well.
        #i.e. for [discord.SelectOption(label=menu_item[0], description=menu_item[1]) for menu_item in self.users_menu_items]

        # The placeholder is what will be shown when no option is selected.
        # The min and max values indicate we can only pick one of the three options.
        # The options parameter, contents shown above, define the dropdown options.
        super().__init__(
            placeholder="Choose your a menu item...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        self.value = self.values[0]
        await interaction.response.send_message(content='Menu Item Selected...', ephemeral=True, delete_after=3) #could make 0 so it dissapears immediately
        self.view.disable_all_items()
        self.view.stop()


# Defines a simple View that allows the user to use the Select menu.
@asyncinit
class DropdownView(discord.ui.View):
    async def __init__(self, interaction, *args, **kwargs) -> None:
        super().__init__(await Dropdown(interaction))

        # Uses the one-liner from example in dropdown.py
        # Passes the interaction object from calling interaction




@bot.slash_command(
    name = "dynamic_menu",
    description = "Dynamic Menu Command"
)
async def user_dynamic_menu(interaction: discord.Interaction):
    """Sends a message with our dropdown that contains colour options."""
    await interaction.response.defer(ephemeral=True)
    view = await DropdownView(interaction)
    await interaction.followup.send(view=view)
    await view.wait()
    # Waits for a menu selection
    selected_menu_item = view.children[0].value
    # selected menu item is stored in selected_menu_item variable for further processing
    await interaction.followup.send(content=f'You Selected {selected_menu_item}')
    # In this example, we send a follow up message displaying the selected item
    return




@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")




bot.run(input('Please provide your bot token: '))
