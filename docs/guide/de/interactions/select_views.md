# Auswahlmenüs
Eine Einführung in Auswahlmenüs für Anfänger und fortgeschrittene Benutzer von Pycord

Auswahlmenüs sind klassenbasiert, ähnlich wie Buttons. Sie sollten also zuerst eine Klasse mit Ihrer Auswahlansicht erstellen
```py
class my_view_name(discord.ui.Select):
    def __init__(self)
```

Dann erstellen Sie eine Liste mit Ihren Select Optionen

Diese Liste sollte alles vom Label bis zum Emoji enthalten.
````py
options = [
    discord.SelectOption(
        label="mein_label_name", description="meine_option_description", emoji="dein_emoji"
    ),
]
```
Und Sie können noch mehr hinzufügen.

Sie können maximal 25 hinzufügen.

Dann können Sie einen Interaktions-Callback in der gleichen Klasse erstellen

```py
async def callback(self, interaction)
    await interaction.response.send_message(f "ihre_nachricht")
```

Erstellen Sie dann eine weitere Klasse, die View untergeordnet ist.

Dann fügen Sie Ihre Select View als Element hinzu.
```py
class my_view_name_View(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(mein_ansicht_name())
```

Jetzt kannst du deinen Befehl mit deiner Ansicht machen

```py
@bot.slash_command(guild_ids=[...]) # Begrenzt die Anzahl der Gilden mit dem Befehl
async def mein_befehl_name(ctx):
    await ctx.respond(f "your_message", view=my_view_name_View())
```

Und das war's, das ist alles an Selects in Pycord!