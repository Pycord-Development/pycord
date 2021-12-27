# Button Menus
A Primer For Beginners & Advanced Users To Buttons In Pycord

### Basic Reply Button
First you will want to A Class with your view
like so:

```py
class My_View_Name(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Green",
        style=discord.ButtonStyle.green,
        custom_id="persistent_view:green",
    )
    async def green(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Press Me!", ephemeral=True) # Makes The Message Ephemeral.
```

Then you would want to make a command and send your message with the view like:
```py
ctx.send("Your_Message", view=My_View_Name())
```

And that's it! you have made your first button with Pycord

### How to disable a button

You will first want to make your Button.

```py
@discord.ui.button(label="button_name", style=discord.ButtonStyle.green)
async def disable(self, button: discord.ui.Button, interaction: discord.Interaction):
```

Then make this function which would disable the button after a certain number of seconds.

```py
number = int(button.label) if button.label else 0
if number + 1 >= 5:
    button.style = discord.ButtonStyle.green
    button.disabled = True
button.label = str(number + 1)

# Make sure to update the message with our updated selves
await interaction.response.edit_message(view=self)
```

And send your message
```py
ctx.send("your_message", view=my_view_name())