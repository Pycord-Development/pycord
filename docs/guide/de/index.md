# Leitfaden
Der offizielle Leitfaden für Pycord

# Kurzer Tipp
Pycord wird mit automatischer Dateierzeugung über die Eingabeaufforderung geliefert.

Beispiel für einige Befehle, die Sie verwenden können:

## ``python -m py-cord newbot (args)``

#### Args:

- Name
  - Ihr Projektname
--gesharded
   - Ob Ihr Bot sharded sein soll oder nicht
--prefix
   - Dein Bot-Präfix

## ``python -m py-cord newcog (args)``

#### Args:

- Name
   - Der Name deines Cogs

- Verzeichnis 
   - Cogs Verzeichnis

--voll
   - Alle Funktionen von Cogs abrufen

--class-name
   - Name Ihrer Cogs-Klasse 

## Bevor Sie beginnen...
Pycord hat viele Funktionen, die für eine Person, die gerade erst mit Python anfängt, zu fortgeschritten sind,
Wir würden vorschlagen, dass Sie sich die Grundkenntnisse von Python aneignen, bevor Sie beginnen. Es gibt eine Menge Tutorials, denen Sie folgen können, und wir würden vorschlagen, dass Sie mit kleinen Projekten beginnen und dann nach und nach größer werden.

### Wie viel Python muss ich wissen?

- Der Unterschied zwischen Instanzen und Klassenattributen.
    - z.B. `Gildenname` vs. `Discord.Gildenname` oder jede Variation davon.
- Wie man Datenstrukturen in der Sprache verwendet.
    - `dict`/`tuple`/`list`/`str`/`...`
- Wie man Ausnahmen wie `NameError` oder `SyntaxError` löst.
- Wie man Tracebacks liest und versteht.

Diese Liste deckt **nicht** alles ab, was Sie wissen sollten, bevor Sie Pycord benutzen. Wir empfehlen, dass Sie zumindest diese Punkte kennen, bevor Sie versuchen, einen Bot in Pycord zu erstellen.

## Leitfaden-Liste

```{eval-rst}
Der Leitfaden, wie Sie es versuchen können :doc:`Start/Installation>`

Wenn Sie nicht wissen, wie Sie einen Bot in Discord erstellen können -> :doc:`starting-out/making-a-bot`

Und wenn du nicht weißt, welche Dateien du beim Start auswählen sollst, empfehlen wir dir :doc:`starting-out/initial-files`

Der Pycord :doc:`interactions/slash_commands` Guide.

Der Pycord :doc:`interactions/context_menus` Leitfaden.

Der Pycord :doc:`interactions/button_views` Leitfaden.

Der Pycord :doc:`interactions/select_views` Leitfaden.

Eine Sache, die Sie sich vielleicht ansehen sollten, ist :doc:`ext/commands/index`.

:doc:`misc/intents`

Sie sollten :doc:`misc/logging` in Pycord ausprobieren.
```
<!--:doc:`misc/webhooks` Guide, Das Fertigstellen ist nicht so wichtig, wenn jemand will, kann er es fertigstellen.-->