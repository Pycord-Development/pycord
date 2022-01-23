# Context Menus
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
.. image:: /images/guide/user_command.png
    :alt: User Command Image
```

### Message Commands
Message Commands are again Simular to slash & user commands and you would make them like so:

```{eval-rst}

.. warning::

    Message Commands have to take in message

```
```py
@bot.message_command(name="Show Message ID") # Creates a global message command
async def message_id(ctx, message: discord.Message): # Message commands return the message
    await ctx.respond(f"{ctx.author.name}, here's the message id: {message.id}!")
```

And it should return with the following:
```{eval-rst}
.. image:: /images/guide/message_command.png
    :alt: Message Command Image
```