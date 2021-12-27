# Slash-Befehle
Eine Einführung in die Slash-Befehle für Fortgeschrittene und neue Benutzer

### Grundlegende Slash-Befehle
Slash-Befehle sind den Legacy-Befehlen sehr ähnlich

Anstelle von `@bot.command` sollten Sie `@bot.slash_command` verwenden.

Die meisten Nachrichtenmethoden von Context wurden zu `ctx.respond("message", view=None)` umgewandelt.

Aber es ist sehr einfach, sie zu erstellen:

``py
@bot.slash_command(guild_ids=[...]) # begrenzt die verfügbaren Gilden-IDs
async def example(ctx):
    """Beispiel Beschreibung"""
    await ctx.respond("Nachricht", view=None) # Nachricht senden
```

### Autocompleted Command
Autovervollständigte Nachrichten sind in Pycord implementiert!

Sie sind sehr einfach zu erstellen
Sie müssen zuerst eine Liste von autovervollständigten Wörtern erstellen
````py
meine_liste = [
    "..."
    "..."
]
```

Erstellen Sie dann eine Liste von Benutzer-IDs, die dies verwenden können:

```py
allowed_users_list = [
    "..."
    "..."
]
```

Dann erstellen Sie eine Funktion, die nach Ergebnissen in der Liste sucht:

```py
async def list_search(ctx: discord.AutocompleteContext):
    """Return's A List Of Autocomplete Results"""
    return [
        thing for thing in my_list if ctx.interaction.user.id in allowed_users_list
    ]
```

Jetzt können Sie Ihren Befehl 

```py
@bot.slash_command(name="ac_example")
async def autocomplete_example(
    ctx: discord.ApplicationContext,
    choice: Option(str, "was wird deine Wahl sein!", autocomplete=list_search),
):
    await ctx.respond(f "Du hast {Wahl} gewählt!")
```

### Verwaltung von Slash-Befehlsberechtigungen

Zuerst müssen Sie einen Slash-Befehl erstellen
```py
@bot.slash_command(guild_ids=[...]) # Begrenzt Gilden mit diesem Befehl
```

Dann fügen Sie im unteren Bereich hinzu

```py
@Permissions.foo() # Ersetze foo durch has_role oder is_user etc.
```