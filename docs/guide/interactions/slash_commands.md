# Slash Commands
A Primer to Slash Commands for advanced & new users

### Basic Slash Command
Slash Commands are very close to Legacy commands

Instead of using `@bot.command` you will want to use `@bot.slash_command`

Most Of Context's message methods were stripped to `ctx.respond("message", view=None)`

But it is very easy to make them:

```py
@bot.slash_command(guild_ids=[...]) # limits Guild ID's available
"""Example Description"""
async def example(ctx):
    await ctx.respond("message", view=None) # Send Message
```

### Autocompleted Command
Autocompleted messages are implemented into Pycord!

They are very easy to make
you would first want to make a list of autocompleted words
```py
my_list = [
    "..."
    "..."
]
```

Then make a list of User id's which can use this:

```py
allowed_users_list = [
    "..."
    "..."
]
```

Then make a function which would search for results in the list:

```py
async def list_search(ctx: discord.AutocompleteContext):
    """Return's A List Of Autocomplete Results"""
    return [
        color for color in my_list if ctx.interaction.user.id in allowed_users_list
    ]
```

Now you can make your command 

```py
@bot.slash_command(name="ac_example")
async def autocomplete_example(
    ctx: discord.ApplicationContext,
    choice: Option(str, "what will be your choice!", autocomplete=list_search),
):
    await ctx.respond(f"You picked {choice}!")
```

### Managing Slash Command Permissions

You will first want to make a slash command
```py
@bot.slash_command(guild_ids=[...]) # Limits guilds with this command
```

Then in the bottom add

```py
@permissions.foo() # Replace foo with has_role or is_user etc.
```
