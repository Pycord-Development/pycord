# Views
The Guide To Using Views In Pycord!

## Select Menus
A Primer On Select Menus For Beginners & Advanced Users Of Pycord

## Button Menus
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
        await interaction.response.send_message("Press Me!", ephemeral=True)
```

Then you would want to make a command and send your message with the view like:
```py
ctx.send("Your_Message", view=My_View_Name())
```

And that's it! you have made your first button with Pycord
## Ext.Menus Guide

Coming *Soon*