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

Then make a function which would search for results in the list:

```py
async def list_search(ctx: discord.AutocompleteContext):
    """Return's A List Of Autocomplete Results"""
    return [
        color for color in LOTS_OF_COLORS if ctx.interaction.user.id in BASIC_ALLOWED
    ]
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



### Message Commands
Message Commands are again Simular to slash & user commands and you would make them like so:

```py
@bot.message_command(name="Show Message ID") # Creates a global message command
async def message_id(ctx, message: discord.Message): # Message commands return the message
    await ctx.respond(f"{ctx.author.name}, here's the message id: {message.id}!")
```