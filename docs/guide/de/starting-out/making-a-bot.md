```{eval-rst}
:orphan:

.. _discord-intro:

Erstellen eines Bot-Kontos
========================

Um mit der Bibliothek und der Discord-API im Allgemeinen arbeiten zu können, müssen wir zunächst ein Discord-Bot-Konto erstellen.

Das Erstellen eines Bot-Kontos ist ein ziemlich unkomplizierter Prozess.

1. Vergewissern Sie sich, dass Sie auf der Discord-Website <https://discord.com>`_ angemeldet sind.
2. Navigieren Sie zur `Anwendungsseite <https://discord.com/developers/applications>`_.
3. Klicken Sie auf die Schaltfläche "Neue Anwendung".

    ...Bild:: /images/discord_create_app_button.png
        :alt: Die Schaltfläche "Neue Anwendung".

4. Geben Sie der Anwendung einen Namen und klicken Sie auf "Erstellen".

    ... Bild:: /images/discord_create_app_form.png
        :alt: Das neu ausgefüllte Antragsformular.

5. Erstellen Sie einen Bot-Benutzer, indem Sie zur Registerkarte "Bot" navigieren und auf "Bot hinzufügen" klicken.

    - Klicken Sie auf "Yes, do it!", um fortzufahren.

    .. image:: /images/discord_create_bot_user.png
        :alt: Die Schaltfläche "Bot hinzufügen".
6. Vergewissern Sie sich, dass **Public Bot** angekreuzt ist, wenn Sie möchten, dass andere Personen Ihren Bot einladen können.

    - Vergewissern Sie sich auch, dass **OAuth2 Code Grant** nicht angekreuzt ist, es sei denn, Sie
      wenn Sie nicht gerade einen Dienst entwickeln, der dies erfordert. Wenn Sie sich nicht sicher sind, lassen Sie es **unangekreuzt**.

    ...Bild:: /images/discord_bot_user_options.png
        :alt: So sollten die Bot-Benutzeroptionen für die meisten Menschen aussehen.

7. Kopieren Sie das Token über die Schaltfläche "Kopieren".

    - Dies ist nicht das Client-Geheimnis auf der Seite "Allgemeine Informationen".

    ...Warnung::

        Beachten Sie, dass dieses Token im Wesentlichen das Passwort Ihres Bots ist.
        Passwort ist. Sie sollten es **niemals** an eine andere Person weitergeben. Wenn Sie das tun,
        kann sich jemand in Ihren Bot einloggen und bösartige Dinge tun, wie z.B.
        Server zu verlassen, alle Mitglieder innerhalb eines Servers zu sperren oder böswillige Pings an alle zu senden.

        Die Möglichkeiten sind endlos, also **geben Sie dieses Token nicht weiter**.

        Wenn Sie Ihren Token versehentlich weitergegeben haben, klicken Sie so schnell wie möglich auf die Schaltfläche "Neu generieren".
        so schnell wie möglich. Dadurch wird Ihr alter Token widerrufen und ein neuer Token generiert.
        Nun müssen Sie sich mit dem neuen Token anmelden.

Und das war's. Sie haben jetzt ein Bot-Konto und können sich mit diesem Token anmelden.

.. _discord_invite_bot:

Ihren Bot einladen
-------------------

Sie haben also einen Bot-Benutzer erstellt, aber er befindet sich nicht auf einem Server.

Wenn Sie Ihren Bot einladen möchten, müssen Sie eine Einladungs-URL für ihn erstellen.

1. Stellen Sie sicher, dass Sie auf der `Discord-Website <https://discord.com>`_ angemeldet sind.
2. Navigieren Sie zur `Anwendungsseite <https://discord.com/developers/applications>`_.
3. Klicke auf die Seite deines Bots.
4. Erweitern Sie den Reiter "OAuth2" und klicken Sie auf "URL Generator".

    ...Bild:: /images/discord_oauth2.png
        :alt: So sollte die OAuth2-Registerkarte aussehen.

5. Aktivieren Sie die Kontrollkästchen "bot" und "applications.commands" unter "scopes".

    .. image:: /images/discord_oauth2_scope.png
        :alt: Das Kontrollkästchen für den Geltungsbereich, wenn "bot" und "applications.commands" angekreuzt sind.

6. Aktivieren Sie unter "Bot Permissions" die für die Funktion Ihres Bots erforderlichen Berechtigungen.

    - Bitte beachten Sie die Konsequenzen, wenn Sie für Ihren Bot die Berechtigung "Administrator" benötigen.

    - Bot-Besitzer müssen für bestimmte Aktionen und Berechtigungen 2FA aktiviert haben, wenn sie auf Servern hinzugefügt werden, auf denen Server-weite 2FA aktiviert ist. Weitere Informationen finden Sie auf der `2FA-Supportseite <https://support.discord.com/hc/en-us/articles/219576828-Setting-up-Two-Factor-Authentication>`_.

    ...Bild:: /images/discord_oauth2_perms.png
        :alt: Die Kontrollkästchen für die Berechtigungen mit einigen aktivierten Berechtigungen.

7. Nun kann die resultierende URL verwendet werden, um Ihren Bot zu einem Server hinzuzufügen. Kopieren Sie die URL und fügen Sie sie in Ihren Browser ein, wählen Sie einen Server aus, zu dem Sie den Bot einladen möchten, und klicken Sie auf "Autorisieren".


...Hinweis::

    Die Person, die den Bot hinzufügt, muss über die Berechtigung "Server verwalten" verfügen, um dies zu tun.

Wenn Sie diese URL dynamisch zur Laufzeit innerhalb Ihres Bots generieren möchten und die
Schnittstelle :class:`discord.Permissions` verwenden, können Sie :func:`discord.utils.oauth_url` verwenden.
```