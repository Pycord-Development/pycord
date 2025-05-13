import discord


# Defines a custom Select containing colour options
# that the user can choose. The callback function
# of this class is called when the user changes their choice.
class Dropdown(discord.ui.Select):
    def __init__(self, bot_: discord.Bot):
        # For example, you can use self.bot to retrieve a user or perform other functions in the callback.
        # Alternatively you can use Interaction.client, so you don't need to pass the bot instance.
        self.bot = bot_
        # Set the options that will be presented inside the dropdown:
        options = [
            discord.SelectOption(label="Red", description="Your favourite colour is red", emoji="🟥"),
            discord.SelectOption(label="Green", description="Your favourite colour is green", emoji="🟩"),
            discord.SelectOption(label="Blue", description="Your favourite colour is blue", emoji="🟦"),
        ]

        # The placeholder is what will be shown when no option is selected.
        # The min and max values indicate we can only pick one of the three options.
        # The options parameter, contents shown above, define the dropdown options.
        super().__init__(
            placeholder="Choose your favourite colour...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        await interaction.response.send_message(f"Your favourite colour is {self.values[0]}")


# Defines a simple View that allows the user to use the Select menu.
class DropdownView(discord.ui.View):
    def __init__(self, bot_: discord.Bot):
        self.bot = bot_
        super().__init__()

        # Adds the dropdown to our View object
        self.add_item(Dropdown(self.bot))

        # Initializing the view and adding the dropdown can actually be done in a one-liner if preferred:
        # super().__init__(Dropdown(self.bot))


bot = discord.Bot(debug_guilds=[...])


@bot.slash_command()
async def colour(ctx: discord.ApplicationContext):
    """Sends a message with our dropdown that contains colour options."""

    # Create the view containing our dropdown
    view = DropdownView(bot)

    # Sending a message containing our View
    await ctx.respond("Pick your favourite colour:", view=view)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


bot.run("TOKEN")
