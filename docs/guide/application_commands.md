# Application Commands
The Application Command Guide!

## Slash Commands
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

## Context Menu's
Context Menu commands are very simular to slash commands with the only real difference in code being that they return `member` or `message`

### User Commands
User Commands are very simular to Slash commands and the same as message commands

Only difference being you have to return the user in some way:

```py
@bot.user_command(guild_ids=[...]) # Limits The Guilds With this Menu  
async def mention(ctx, member: discord.Member):  # User Commands return the member
    await ctx.respond(f"{ctx.author.name} just mentioned {member.mention}!")
```

And it should return the following:
```{eval-rst}
.. image:: /images/user_command.png
    :alt: User Command Image
```

### Message Commands
Message Commands are again Simular to slash & user commands and you would make them like so:

```py
@bot.message_command(name="Show Message ID") # Creates a global message command
async def message_id(ctx, message: discord.Message): # Message commands return the message
    await ctx.respond(f"{ctx.author.name}, here's the message id: {message.id}!")
```

And it should return with the following:
```{eval-rst}
.. image:: /images/message_command.png
    :alt: Message Command Image
```
