.. currentmodule:: discord

Client Objects
==============

Bots
----

.. attributetable:: Bot
.. autoclass:: Bot
    :members:
    :inherited-members:
    :exclude-members: command, event, message_command, slash_command, user_command, listen

    .. automethod:: Bot.command(**kwargs)
        :decorator:

    .. automethod:: Bot.event()
        :decorator:

    .. automethod:: Bot.message_command(**kwargs)
        :decorator:

    .. automethod:: Bot.slash_command(**kwargs)
        :decorator:

    .. automethod:: Bot.user_command(**kwargs)
        :decorator:

    .. automethod:: Bot.listen(name=None)
        :decorator:

.. attributetable:: AutoShardedBot
.. autoclass:: AutoShardedBot
    :members:


Clients
-------

.. attributetable:: Client
.. autoclass:: Client
    :members:
    :exclude-members: fetch_guilds, event

    .. automethod:: Client.event()
        :decorator:

    .. automethod:: Client.fetch_guilds
        :async-for:

.. attributetable:: AutoShardedClient
.. autoclass:: AutoShardedClient
    :members:
