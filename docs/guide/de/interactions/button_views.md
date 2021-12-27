# Schaltflächen-Menüs
Eine Fibel für Anfänger und Fortgeschrittene zu Schaltflächen in Pycord

### Grundlegende Antwort-Schaltfläche
Zuerst werden Sie eine Klasse mit Ihrer Ansicht erstellen wollen
etwa so:

```py
class My_View_Name(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Grün",
        style=discord.ButtonStyle.green,
        custom_id="persistent_view:green",
    )
    async def green(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Press Me!", ephemeral=True) # Macht die Nachricht flüchtig.
```

Dann würden Sie einen Befehl erstellen und Ihre Nachricht mit der Ansicht wie folgt senden wollen:
```py
ctx.send("Ihre_Mitteilung", view=Mein_View_Name())
```

Und das war's! Sie haben Ihren ersten Button mit Pycord erstellt

### Wie man einen Button deaktivieren kann

Sie werden zuerst Ihren Button erstellen wollen.

```py
@discord.ui.button(label="button_name", style=discord.ButtonStyle.green)
async def disable(self, button: discord.ui.Button, interaction: discord.Interaction):
```

Dann mache diese Funktion, die den Button nach einer bestimmten Anzahl von Sekunden deaktiviert.

```py
number = int(button.label) if button.label else 0
wenn Zahl + 1 >= 5:
    button.style = discord.ButtonStyle.green
    button.disabled = Wahr
button.label = str(number + 1)

# Stellen Sie sicher, dass die Nachricht mit unserem aktualisierten Selbst aktualisiert wird
await interaction.response.edit_message(view=self)
```

Und sende deine Nachricht
```py
ctx.send("ihre_nachricht", view=meine_ansicht_name())
```