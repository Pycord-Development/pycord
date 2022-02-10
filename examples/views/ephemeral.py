import pycord
from pycord.ext import commands


class EphemeralCounterBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("$"))

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")


# Define a simple View that gives us a counter button
class Counter(pycord.ui.View):

    # Define the actual button
    # When pressed, this increments the number displayed until it hits 5.
    # When it hits 5, the counter button is disabled and it turns green.
    # NOTE: The name of the function does not matter to the library
    @pycord.ui.button(label="0", style=pycord.ButtonStyle.red)
    async def count(self, button: pycord.ui.Button, interaction: pycord.Interaction):
        number = int(button.label) if button.label else 0
        if number + 1 >= 5:
            button.style = pycord.ButtonStyle.green
            button.disabled = True
        button.label = str(number + 1)

        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(view=self)


# Define a View that will give us our own personal counter button
class EphemeralCounter(pycord.ui.View):
    # When this button is pressed, it will respond with a Counter view that will
    # give the button presser their own personal button they can press 5 times.
    @pycord.ui.button(label="Click", style=pycord.ButtonStyle.blurple)
    async def receive(
        self, button: pycord.ui.Button, interaction: pycord.Interaction
    ):
        # ephemeral=True makes the message hidden from everyone except the button presser
        await interaction.response.send_message(
            "Enjoy!", view=Counter(), ephemeral=True
        )


bot = EphemeralCounterBot()


@bot.command()
async def counter(ctx: commands.Context):
    """Starts a counter for pressing."""
    await ctx.send("Press!", view=EphemeralCounter())


bot.run("token")
