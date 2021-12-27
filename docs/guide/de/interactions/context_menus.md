# Kontextmenüs
Kontextmenü-Befehle sind den Schrägstrich-Befehlen sehr ähnlich. Der einzige wirkliche Unterschied im Code besteht darin, dass sie "Mitglied" oder "Nachricht" zurückgeben.

### Benutzer-Befehle
Benutzerbefehle sind den Schrägstrich-Befehlen sehr ähnlich und entsprechen den Nachrichtenbefehlen.

Der einzige Unterschied besteht darin, dass man den Benutzer auf irgendeine Weise zurückgeben muss:

```py
@bot.user_command(guild_ids=[...]) # Begrenzt die Gilden mit diesem Menü  
async def mention(ctx, member: discord.Member):  # Benutzerkommandos geben das Mitglied zurück
    await ctx.respond(f"{ctx.author.name} hat gerade {member.mention} erwähnt!")
```

Und es sollte das Folgende zurückgeben:
```{eval-rst}
...image:: /images/guide/user_command.png
    :alt: Benutzerbefehl Bild
```

### Nachrichten-Befehle
Nachrichtenbefehle sind wiederum ähnlich wie Schrägstrich- und Benutzerkommandos, und Sie würden sie wie folgt erstellen:

```{eval-rst}

...Warnung::

    Message Commands muessen eine Nachricht enthalten

```
```py
@bot.message_command(name="Show Message ID") # Erzeugt einen globalen Nachrichtenbefehl
async def message_id(ctx, message: discord.Message): # Nachrichtenbefehle geben die Nachricht zurück
    await ctx.respond(f"{ctx.author.name}, hier ist die Nachrichten-ID: {message.id}!")
```

Und es sollte mit folgendem Ergebnis zurückkommen:
```{eval-rst}
...image:: /images/guide/message_command.png
    :alt: Message Command Image
```