# Select Menus
A Primer On Select Menus For Beginners & Advanced Users Of Pycord

Select Menus are class based like how buttons are, So you would want to first make a class with your select view
```py
class my_view_name(discord.ui.Select):
    def __init__(self)
```

Then make a list of your Select Options

This list should hold anything from the label to Emoji.
```py
options = [
    discord.SelectOption(
        label="my_label_name", description="my_option_description", emoji="your_emoji"
    ),
]
```
And you can add more.

The limit you can put is 25.

Then you can make an interaction callback in the same class

```py
async def callback(self, interaction)
    await interaction.response.send_message(f"your_message")
```

Then make another class which subclasses View.

Then add your Select View as a item.
```py
class my_view_name_View(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(my_view_name())
```

Now you can make your command With your view

```py
@bot.slash_command(guild_ids=[...]) # Limits Number Of Guilds With The Command
async def my_command_name(ctx):
    await ctx.respond(f"your_message", view=my_view_name_View())
```

And thats it that is all of selects in Pycord!

We hope you learn't how to make selects or advanced your knowledge to with this.