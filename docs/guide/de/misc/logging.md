```{eval-rst}
:orphan:

.. versionadded:: 0.6.0
.. _logging_setup:

Einrichten der Protokollierung
==================

*Pycord* protokolliert Fehler und Debug-Informationen über das :mod:`logging` python
Modul. Es wird dringend empfohlen, dass das Logging-Modul
konfiguriert ist, da keine Fehler oder Warnungen ausgegeben werden, wenn es nicht konfiguriert ist.
Die Konfiguration des ``logging``-Moduls kann so einfach sein wie::

    import logging

    logging.basicConfig(level=logging.INFO)

Wird am Anfang der Anwendung platziert. Dies wird die Logs von
discord sowie andere Bibliotheken, die das ``logging`` Modul benutzen
verwenden, direkt auf der Konsole aus.

Das optionale ``Level`` Argument spezifiziert, welches Level von Ereignissen protokolliert werden soll
ausgeben soll und kann einer der Werte ``CRITICAL``, ``ERROR``, ``WARNING``, ``INFO``, und
``DEBUG`` sein und ist, wenn nicht angegeben, auf ``WARNING`` voreingestellt.

Weitergehende Einstellungen sind mit dem Modul :mod:`logging` möglich. Für
zum Beispiel, um die Logs in eine Datei namens ``discord.log`` zu schreiben, anstatt
in eine Datei namens ``discord.log`` zu schreiben, anstatt sie auf der Konsole auszugeben, kann das folgende Snippet verwendet werden::

    import discord
    importiere logging

    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

Dies wird empfohlen, besonders auf ausführlichen Ebenen wie ``INFO``
und ``DEBUG``, da eine Menge Ereignisse protokolliert werden und es die
stdout Ihres Programms verstopfen würde.



Für weitere Informationen lesen Sie bitte die Dokumentation und das Tutorial des
:mod:`Logging`-Moduls.
```