# Using Cogs in Pycord
The ``ext.commands`` module provided by Pycord introduces a `Cog` system allowing you to make commands of any kind or even events in another file.
# Basics
A basic `Cog` would just be subclassing the `commands.Cog` class, like so:
```py
from discord.ext import commands

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
```
Then to add it as a `Cog` make the function!
```py
def setup(bot):
    bot.add_cog(MyCog(bot))
```
Then finally just add it to your load_extensions:
```py
bot.load_extension("my_cog")
```
Then that's it, You now have a `Cog`!

# How to make a command
Making commands are as-easy as normal,
only difference is using `@commands.command` instead of `@bot.command` inside your `Cog` like so:
```py
@commands.command()
async def my_command(self, ctx):
    ...
```
