```{eval-rst}
:orphan:

.. currentmodule:: discord

.. _intro:

Einführung
============

Dies ist die Dokumentation für Pycord, eine Bibliothek für Python zur Unterstützung
zur Erstellung von Anwendungen, die die Discord-API nutzen.

Voraussetzungen
-------------

Pycord funktioniert mit Python 3.8 oder höher. Unterstützung für frühere Versionen von Python
ist nicht vorgesehen. Python 2.7 oder niedriger wird nicht unterstützt. Python 3.7 oder niedriger wird nicht unterstützt.


.. _installieren:

Installation von
-----------

Sie können die Bibliothek direkt von PyPI beziehen: ::

    python3 -m pip install -U py-cord

Wenn Sie Windows verwenden, sollten Sie stattdessen folgendes verwenden: ::

    py -3 -m pip install -U py-cord


Um zusätzliche Pakete für die Beschleunigung zu installieren, sollten Sie ``py-cord[speed]`` anstelle von ``py-cord`` verwenden, z.B. ::

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "py-cord[speed]"
    
    # Windows
    py -3 -m pip install -U py-cord[Geschwindigkeit]


Um Sprachunterstützung zu erhalten, sollten Sie ``py-cord[voice]`` anstelle von ``py-cord`` verwenden, z.B.::

    python3 -m pip install -U py-cord[voice]

In Linux-Umgebungen erfordert die Installation von voice die Beschaffung der folgenden Abhängigkeiten:

- `libffi <https://github.com/libffi/libffi>`_
- `libnacl <https://github.com/saltstack/libnacl>`_
- `python3-dev <https://packages.debian.org/python3-dev>`_

Für ein Debian-basiertes System, wird der folgende Befehl diese Abhängigkeiten erhalten:

.. code-block:: shell

    $ apt install libffi-dev libnacl-dev python3-dev

Denken Sie daran, Ihre Berechtigungen zu überprüfen!

Virtuelle Umgebungen
~~~~~~~~~~~~~~~~~~~~

Manchmal möchte man verhindern, dass Bibliotheken die Systeminstallationen verunreinigen oder eine andere Version von
als die auf dem System installierten Bibliotheken. Es kann auch sein, dass Sie keine Berechtigung haben, Bibliotheken systemweit zu installieren.
Zu diesem Zweck verfügt die Standardbibliothek ab Python 3.3 über ein Konzept namens "Virtual Environment", das
diese getrennten Versionen zu verwalten.

Ein ausführlicheres Tutorial findet sich unter :doc:`py:tutorial/venv`.

Aber für die schnelle und schmutzige Seite:

1. Wechseln Sie in das Arbeitsverzeichnis Ihres Projekts:

    .. code-block:: shell

        $ cd your-bot-source
        $ python3 -m venv bot-env

2. Aktivieren Sie die virtuelle Umgebung:

    .. code-block:: shell

        $ source bot-env/bin/activate

    Unter Windows aktivieren Sie sie mit:

    .. code-block:: shell

        $ bot-env\Scripts\activate.bat

3. Verwenden Sie pip wie gewohnt:

    .. code-block:: shell

        $ pip install -U py-cord

Glückwunsch! Sie haben nun eine virtuelle Umgebung eingerichtet.

Grundlegende Konzepte
--------------

Pycord dreht sich um das Konzept von :ref:`Events <discord-api-events>`.
Ein Ereignis ist etwas, auf das Sie hören und auf das Sie dann reagieren. Zum Beispiel, wenn eine Nachricht
geschieht, erhalten Sie ein Ereignis, auf das Sie reagieren können.

Ein kurzes Beispiel, um zu zeigen, wie Ereignisse funktionieren:

.. code-block:: python3

    import discord

    class MyClient(discord.Client):
        async def on_ready(self):
            print(f'Angemeldet als {self.user}!')

        async def on_message(self, message):
            print(f'Nachricht von {message.author}: {message.content}')

    client = MyClient()
    client.run('mein Token kommt hier hin')
```