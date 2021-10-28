:orphan:

.. currentmodule:: discord
.. versionadded:: 2.0
.. _application_commands:

Application Commands
=====================

Application commands are commands that an application can register to Discord. They provide users a way of interacting
directly with your application that feels deeply integrated into Discord.

Application commands can be used with either :class:`.Bot` or :class:`.ext.commands.Bot`.

.. code-block:: python3
    import discord
    bot = discord.Bot()

    @bot.command() # creates slash command by default
    async def foo(ctx, arg):
        await ctx.respond(arg)

    # or

    from discord.ext import commands
    bot = commands.Bot()

    @bot.slash_command()
    async def foo(ctx, arg):
        await ctx.respond(arg)

ApplicationCommand
~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationCommand

.. autoclass:: ApplicationCommand
    :members:

SlashCommand
~~~~~~~~~~~~~

.. attributetable:: SlashCommand

.. autoclass:: SlashCommand
    :members:

SlashCommandGroup
~~~~~~~~~~~~~~~~~~

.. attributetable:: SlashCommandGroup

.. autoclass:: SlashCommandGroup
    :members:

Option
~~~~~~~

.. attributetable:: Option

.. autoclass:: Option
    :members:

OptionChoice
~~~~~~~~~~~~~

.. attributetable:: OptionChoice

.. autoclass:: OptionChoice
    :members:

UserCommand
~~~~~~~~~~~~

.. attributetable:: UserCommand

.. autoclass:: UserCommand
    :members:

MessageCommand
~~~~~~~~~~~~~~~

.. attributetable:: MessageCommand

.. autoclass:: MessageCommand
    :members:

ApplicationContext
~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationContext

.. autoclass:: ApplicationContext
    :members:
