.. currentmodule:: discord

Client Objects
==============

Bots
----

.. attributetable:: Bot
.. autoclass:: Bot
    :members:
    :inherited-members:
    :exclude-members: command, event, message_command, slash_command, user_command, listen, once

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

    .. automethod:: Bot.once(name=None, check=None)
        :decorator:

.. attributetable:: AutoShardedBot
.. autoclass:: AutoShardedBot
    :members:


Clients
-------

.. attributetable:: Client
.. autoclass:: Client
    :members:
    :exclude-members: fetch_guilds, event, once

    .. automethod:: Client.event()
        :decorator:

    .. automethod:: Client.fetch_guilds
        :async-for:

    .. automethod:: Client.once(name=None, check=None)
        :decorator:

.. attributetable:: AutoShardedClient
.. autoclass:: AutoShardedClient
    :members:
