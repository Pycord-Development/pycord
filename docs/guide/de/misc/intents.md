```{eval-rst}
:orphan:

.. currentmodule:: discord
.. versionadded:: 1.5
.. _intents_primer:

Eine Fibel für Gateway-Intents
=============================

In Version 1.5 wird die :class:`Intents` eingeführt. Dies ist eine radikale Veränderung in der Art, wie Bots geschrieben werden. Ein Intent ermöglicht es einem Bot, sich für bestimmte Bereiche von Ereignissen zu registrieren. Die Ereignisse, die den einzelnen Intents entsprechen, werden im individuellen Attribut der :class:`Intents`-Dokumentation dokumentiert.

Diese Intents werden dem Konstruktor von :class:`Client` oder seinen Unterklassen (:class:`AutoShardedClient`, :class:`~.AutoShardedBot`, :class:`~.Bot`) mit dem Argument ``Intents`` übergeben.

Wenn keine Intents übergeben werden, dann werden standardmäßig alle Intents aktiviert, außer den privilegierten Intents, derzeit :attr:`Intents.members`, :attr:`Intents.presences`, und :attr:`Intents.guild_messages`.

Welche Intents werden benötigt?
--------------------------

Die Intents, die für deinen Bot notwendig sind, kannst du nur selbst bestimmen. Jedes Attribut in der Klasse :class:`Intents` dokumentiert, welchen :ref:`Events <discord-api-events>` es entspricht und welche Art von Cache es ermöglicht.

Wenn du zum Beispiel einen Bot haben willst, der ohne spammige Ereignisse wie Anwesenheit oder Tippen funktioniert, dann könnten wir folgendes tun:

.. code-block:: python3
   :emphasize-lines: 7,9,10

    importiere diskord
    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False

    # Irgendwo anders:
    # client = discord.Client(intents=intents)
    # oder
    # from discord.ext import commands
    # bot = commands.Bot(command_prefix='!', intents=intents)

Beachte, dass dies nicht :attr:`Intents.members` oder :attr:`Intents.guild_messages` aktiviert, da sie privilegierte Intents sind.

Ein weiteres Beispiel, das einen Bot zeigt, der sich nur mit Nachrichten und Gildeninformationen beschäftigt:

.. code-block:: python3
   :emphasize-lines: 7,9,10

    importiere diskord
    intents = discord.Intents(messages=True, guilds=True)
    # Wenn Sie auch Reaktionsereignisse wünschen, aktivieren Sie Folgendes:
    # intents.reactions = True

    # irgendwo anders:
    # client = discord.Client(intents=intents)
    # oder
    # from discord.ext import commands
    # bot = commands.Bot(command_prefix='!', intents=intents)

.. _privileged_intents:

Privilegierte Intents
---------------------

Mit der API-Änderung, bei der Bot-Besitzer Intents angeben müssen, wurden einige Intents weiter eingeschränkt und erfordern mehr manuelle Schritte. Diese Intentionen werden **privilegierte Intentionen** genannt.

Eine privilegierte Absicht erfordert, dass Sie zum Entwicklerportal gehen und sie manuell aktivieren. Um privilegierte Intents zu aktivieren, gehen Sie wie folgt vor:

1. Vergewissern Sie sich, dass Sie auf der `Discord-Website <https://discord.com>`_ angemeldet sind.
2. Navigieren Sie zur "Anwendungsseite" <https://discord.com/developers/applications>`_.
3. Klicken Sie auf den Bot, für den Sie privilegierte Intents aktivieren möchten.
4. Navigieren Sie zur Registerkarte Bot auf der linken Seite des Bildschirms.

    ...Bild:: /images/discord_bot_tab.png
        :alt: Die Bot-Registerkarte auf der Anwendungsseite.

5. Scrollen Sie zum Abschnitt "Privilegierte Gateway-Intentionen" und aktivieren Sie die gewünschten Intentionen.

    ... Bild:: /images/discord_privileged_intents.png
        :alt: Der Selektor für privilegierte Gateway-Intentionen.

.. warning::

    Das Aktivieren von privilegierten Intents, wenn dein Bot in mehr als 100 Gilden ist, erfordert eine `Bot-Verifizierung <https://support.discord.com/hc/en-us/articles/360040720412>`_.

.. note::

    Auch wenn Sie Intents über das Entwicklerportal aktivieren, müssen Sie die Intents
    auch durch Code aktivieren.

Brauche ich privilegierte Intents?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dies ist eine schnelle Checkliste, um festzustellen, ob Sie bestimmte privilegierte Intents benötigen.

.. _Bedarf_Anwesenheit_Intent:

Anwesenheits-Intent
+++++++++++++++

- Ob Sie :attr:`Member.status` überhaupt verwenden, um den Status der Mitglieder zu verfolgen.
- Ob Sie :attr:`Member.activity` oder :attr:`Member.activities` verwenden, um die Aktivitäten der Mitglieder zu überprüfen.

.. _need_members_intent:

Mitglied Intent
+++++++++++++

- Ob Sie den Beitritt oder den Austritt eines Mitglieds verfolgen, entspricht den Ereignissen :func:`on_member_join` und :func:`on_member_remove`.
- Ob Sie Mitgliederaktualisierungen wie z.B. Nickname oder Rollenänderungen verfolgen wollen.
- Ob Sie Benutzeraktualisierungen wie Benutzernamen, Avatare, Unterscheidungsmerkmale usw. verfolgen wollen.
- Ob Sie die Gildenmitgliederliste über :meth:`Guild.chunk` oder :meth:`Guild.fetch_members` abfragen wollen.
- Ob du einen hochgenauen Mitglieder-Cache unter :attr:`Guild.members` haben möchtest.

.. _need_message_content_intent:

Nachricht Inhalt Intent
++++++++++++++++++++++

- Ob Sie ein nachrichtenbasiertes Befehlssystem mit ext.commands haben
- Ob Sie das :func:`on_message`-Ereignis für irgendetwas verwenden, z.B. für die automatische Moderation.
- Ob Sie Änderungen oder Löschungen von Nachrichten mit :func:`on_message_edit`, :func:`on_message_delete`, :func:`on_raw_message_edit`, :func:`on_raw_message_delete` verfolgen.
- Ob Sie irgendwelche reaktionsbezogenen Ereignisse verwenden, wie :func:`on_reaction_add`, :func:`on_reaction_remove`, und :func:`on_reaction_clear`

...Hinweis::
    Dies gilt nur für :attr:`Intents.guild_messages`, nicht für :attr:`Intents.dm_messages`. Der Bot kann weiterhin Nachrichteninhalte in DMs empfangen, wenn sie in Gildennachrichten erwähnt werden, und für seine eigenen Gildennachrichten.

.. _intents_member_cache:

Mitglieder-Cache
-------------

Zusammen mit den Intents schränkt Discord nun die Möglichkeit, Mitglieder zu cachen, weiter ein und erwartet, dass Bot-Autoren nur so wenig wie nötig cachen. Um jedoch einen Cache richtig zu pflegen, wird der :attr:`Intents.members` Intent benötigt, um die Mitglieder zu verfolgen, die gegangen sind und sie richtig zu entfernen.

Um den Mitglieder-Cache zu unterstützen, wenn wir keine Mitglieder im Cache benötigen, hat die Bibliothek jetzt ein :class:`MemberCacheFlags` Flag, um den Mitglieder-Cache zu kontrollieren. Die Dokumentationsseite für die Klasse geht auf die spezifischen Richtlinien ein, die möglich sind.

Es sollte beachtet werden, dass bestimmte Dinge keinen Mitglieder-Cache benötigen, da Discord, wenn möglich, vollständige Mitgliederinformationen bereitstellt. Zum Beispiel:

- :func:`on_message` wird :attr:`Message.author` als Mitglied haben, auch wenn der Cache deaktiviert ist.
- Bei :func:`on_voice_state_update` wird der Parameter ``member`` ein Mitglied sein, auch wenn der Cache deaktiviert ist.
- :func:`on_reaction_add` lässt den ``user`` Parameter ein Mitglied sein, wenn er in einer Gilde ist, auch wenn der Cache deaktiviert ist.
- Bei :func:`on_raw_reaction_add` wird :attr:`RawReactionActionEvent.member` in einer Gilde ein Mitglied sein, auch wenn der Cache deaktiviert ist.
- Die Ereignisse zum Hinzufügen von Reaktionen enthalten keine zusätzlichen Informationen, wenn sie in direkten Nachrichten enthalten sind. Dies ist eine Einschränkung von Discord.
- Die Reaktionsentfernungsereignisse enthalten keine Mitgliederinformationen. Dies ist eine Einschränkung von Discord.

Andere Ereignisse, die ein :class:`Member` annehmen, erfordern die Verwendung des Mitglieder-Caches. Wenn absolute Genauigkeit über den Mitglieder-Cache erwünscht ist, dann ist es ratsam, die Absicht :attr:`Intents.members` aktiviert zu haben.

.. _retrieving_members:

Abrufen von Mitgliedern
-----------------------

Wenn der Cache deaktiviert ist oder Sie das Chunking von Gilden beim Start deaktivieren, brauchen wir vielleicht immer noch eine Möglichkeit, Mitglieder zu laden. Die Bibliothek bietet einige Möglichkeiten, dies zu tun:

- :meth:`Guild.query_members`
    - Wird verwendet, um Mitglieder nach einem Präfix abzufragen, das dem Nickname oder Benutzernamen entspricht.
    - Dies kann auch verwendet werden, um Mitglieder nach ihrer Benutzer-ID abzufragen.
    - Dies verwendet das Gateway und nicht HTTP.
- :meth:`Guild.chunk`
    - Dies kann verwendet werden, um die gesamte Mitgliederliste über das Gateway abzurufen.
- :meth:`Guild.fetch_member`
    - Wird verwendet, um ein Mitglied nach ID über die HTTP-API abzurufen.
- :meth:`Guild.fetch_members`
    - wird verwendet, um eine große Anzahl von Mitgliedern über die HTTP-API abzurufen.

Es ist zu beachten, dass das Gateway eine strikte Ratenbegrenzung von 120 Anfragen pro 60 Sekunden hat.

Fehlersuche
---------------

Einige häufige Probleme im Zusammenhang mit der obligatorischen Absichtsänderung.

Wo sind meine Mitglieder hin?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Aufgrund einer :ref:`API-Änderung <intents_member_cache>` zwingt Discord nun Entwickler, die das Zwischenspeichern von Mitgliedern wünschen, sich ausdrücklich dafür zu entscheiden. Dies ist eine von Discord vorgeschriebene Änderung, die nicht umgangen werden kann. Um Mitglieder zurückzubekommen, müssen Sie explizit den :ref:`members privileged intent <privileged_intents>` aktivieren und das Attribut :attr:`Intents.members` auf true ändern.

Zum Beispiel:

.. code-block:: python3
   :emphasize-lines: 3,6,8,9

    importieren diskord
    intents = discord.Intents.default()
    intents.members = True

    # Irgendwo anders:
    # client = discord.Client(intents=intents)
    # oder
    # from discord.ext import commands
    # bot = commands.Bot(command_prefix='!', intents=intents)

Warum braucht ``on_ready`` so lange zum Feuern?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Als Teil der API-Änderung bezüglich der Intents hat Discord auch die Art und Weise geändert, wie Mitglieder zu Beginn geladen werden. Ursprünglich konnte die Bibliothek 75 Gilden auf einmal anfordern und nur Mitglieder von Gilden anfordern, die das Attribut :attr:`Guild.large` auf ``True`` gesetzt haben. Mit der neuen Absichtsänderung schreibt Discord vor, dass wir nur 1 Gilde pro Anfrage senden können. Dies führt zu einer 75-fachen Verlangsamung, die durch die Tatsache, dass *alle* Gilden, nicht nur große Gilden, angefragt werden, noch verstärkt wird.

Es gibt einige Lösungen, um dieses Problem zu beheben.

Die erste Lösung besteht darin, die Absicht der privilegierten Anwesenheit zusammen mit der Absicht der privilegierten Mitglieder anzufordern und beide zu aktivieren. Dadurch kann die anfängliche Mitgliederliste Online-Mitglieder enthalten, genau wie beim alten Gateway. Beachten Sie, dass wir immer noch auf 1 Gilde pro Anfrage beschränkt sind, aber die Anzahl der Gilden, die wir anfordern, ist deutlich reduziert.

Die zweite Lösung ist, das Chunking der Mitglieder zu deaktivieren, indem man ``chunk_guilds_at_startup`` auf ``False`` setzt, wenn man einen Client erstellt. Dann, wenn das Chunking für eine Gilde notwendig ist, kann man die verschiedenen Techniken zum :ref:`Abrufen von Mitgliedern <retrieving_members>` verwenden.

Um die durch die API-Änderung verursachte Verlangsamung zu veranschaulichen, nehmen wir einen Bot, der in 840 Gilden ist und 95 dieser Gilden sind "groß" (über 250 Mitglieder).

Nach dem ursprünglichen System würde dies dazu führen, dass 2 Anfragen zum Abrufen der Mitgliederliste (75 Gilden, 20 Gilden) ungefähr 60 Sekunden dauern würden. Mit :attr:`Intents.members`, aber nicht mit :attr:`Intents.presences`, erfordert dies 840 Anfragen, was bei einem Ratenlimit von 120 Anfragen pro 60 Sekunden bedeutet, dass durch das Warten auf das Ratenlimit insgesamt etwa 7 Minuten Wartezeit anfallen, um alle Mitglieder abzurufen. Mit :attr:`Intents.members` und :attr:`Intents.presences` erhalten wir größtenteils das alte Verhalten, so dass wir nur für die 95 Gilden, die groß sind, Anfragen stellen müssen, das ist etwas weniger als unser Ratenlimit, so dass es nahe an der ursprünglichen Zeit für das Abrufen der Mitgliederliste liegt.

Da diese Änderung von Discord verlangt wird, gibt es leider nichts, was die Bibliothek tun kann, um dies abzumildern.

Wenn Ihnen die Richtung, die Discord mit seiner API einschlägt, wirklich nicht gefällt, können Sie sie über `Support <https://dis.gd/contact>`_ kontaktieren.
```