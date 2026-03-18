.. currentmodule:: discord

Application Commands
====================


Command Permission Decorators
-----------------------------

.. autofunction:: discord.commands.default_permissions
    :decorator:

.. autofunction:: discord.commands.guild_only
    :decorator:

.. autofunction:: discord.commands.is_nsfw
    :decorator:


Commands
--------

Shortcut Decorators
~~~~~~~~~~~~~~~~~~~

.. autofunction:: discord.commands.application_command
    :decorator:

.. autofunction:: discord.commands.command
    :decorator:

.. autofunction:: discord.commands.slash_command
    :decorator:

.. autofunction:: discord.commands.user_command
    :decorator:

.. autofunction:: discord.commands.message_command
    :decorator:

Objects
~~~~~~~

.. attributetable:: ApplicationCommand
.. autoclass:: ApplicationCommand
    :members:

.. attributetable:: SlashCommand
.. autoclass:: SlashCommand
    :members:
    :exclude-members: cog

.. attributetable:: SlashCommandGroup
.. autoclass:: SlashCommandGroup
    :members:

.. attributetable:: UserCommand
.. autoclass:: UserCommand
    :members:

.. attributetable:: MessageCommand
.. autoclass:: MessageCommand
    :members:

Options
-------

Shortcut Decorators
~~~~~~~~~~~~~~~~~~~
.. autofunction:: discord.commands.option
    :decorator:

Objects
~~~~~~~

.. attributetable:: Option
.. autoclass:: Option
    :members:

.. attributetable:: ThreadOption
.. autoclass:: ThreadOption
    :members:

.. attributetable:: OptionChoice
.. autoclass:: OptionChoice
    :members:


Context Objects
---------------

.. attributetable:: ApplicationContext
.. autoclass:: ApplicationContext
    :members:

.. attributetable:: AutocompleteContext
.. autoclass:: AutocompleteContext
    :members:
