import pycord
from pycord.ext import commands


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("$"))

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")


# Define a simple View that gives us a confirmation menu
class Confirm(pycord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # Stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @pycord.ui.button(label="Confirm", style=pycord.ButtonStyle.green)
    async def confirm(
        self, button: pycord.ui.Button, interaction: pycord.Interaction
    ):
        await interaction.response.send_message("Confirming", ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @pycord.ui.button(label="Cancel", style=pycord.ButtonStyle.grey)
    async def cancel(self, button: pycord.ui.Button, interaction: pycord.Interaction):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()


bot = Bot()


@bot.command()
async def ask(ctx: commands.Context):
    """Asks the user a question to confirm something."""
    # We create the view and assign it to a variable so we can wait for it later.
    view = Confirm()
    await ctx.send("Do you want to continue?", view=view)
    # Wait for the View to stop listening for input...
    await view.wait()
    if view.value is None:
        print("Timed out...")
    elif view.value:
        print("Confirmed...")
    else:
        print("Cancelled...")


bot.run("token")
