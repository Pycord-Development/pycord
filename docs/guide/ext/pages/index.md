# Using the ``ext.pages`` module in Pycord
This is a primer to using all that ``ext.pages`` offers you.

# Basics

# Messages
First you will want to tell pages your embeds, like so:
```py
my_pages = [
    "Hey! This is page1",
    "And, this is page2"
]
```
Then define the pages in the `Paginator`, like so:
```py
from discord.ext import pages
scroll = pages.Paginator(pages=my_pages(), show_disabled=False, show_indicator=True)
```
Then customize the buttons to your liking
```py
paginator.customize_button("next", button_label=">", button_style=discord.ButtonStyle.green)
paginator.customize_button("prev", button_label="<", button_style=discord.ButtonStyle.green)
paginator.customize_button("first", button_label="<<", button_style=discord.ButtonStyle.blurple)
paginator.customize_button("last", button_label=">>", button_style=discord.ButtonStyle.blurple)
```