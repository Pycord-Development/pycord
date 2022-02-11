:orphan:

.. currentmodule:: discord
.. versionadded:: 2.0
.. _application_commands:

Application Commands
====================

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

Application Command Types
-------------------------

There are currently three types of application commands: slash, user and message commands.

These have their corresponding decorators.

.. code-block:: python3

    @bot.slash_command()
    async def foo(ctx):
        await ctx.respond("Hello world!")

    @bot.user_command()
    async def bar(ctx, user):
        await ctx.respond(user.id)

    @bot.message_command()
    async def foobar(ctx, message):
        await ctx.respond(message.id)

You can also use the :attr:`.Bot.command` decorator by supplying an application command class.

.. code-block:: python3

    from discord import UserCommand

    @bot.command(..., cls=UserCommand)
    # is the same as
    @bot.user_command(...)

Options
-------

Options are arguments passed into slash commands.

These can be defined as normal function arguments:

.. code-block:: python3

    @bot.slash_command()
    async def say_hello(ctx, name):
        await ctx.respond(f"Hello {name}!")

Typehints can be used to set option types. All option types are listed under :class:`.SlashCommandOptionType`.

.. code-block:: python3

    @bot.slash_command()
    async def foo(ctx, number: int, member: discord.Member):
        # command code

Option fields can be set using :class:`.Option` as the type of the argument.

.. code-block:: python3

    from discord import Option

    @bot.slash_command()
    async def show_color(
        ctx,
        color: Option(str, "Your color choice", choices=["red", "green"]),
    ):
        # command code

Options can also be used with custom converters.

.. code-block:: python3

    from discord.ext.commands import Converter

    class ColorConverter(Converter):
        async def convert(self, ctx, arg):
            if arg == "0":
                return "Black"
            return arg

    @bot.slash_command()
    async def show_color(
        ctx,
        color: Option(ColorConverter, "Your color choice"),
    ):
        # command code

Slash Command Groups
--------------------

Slash command groups allows grouping multiple subcommands under the same parent.

.. code-block:: python3

    my_group = bot.create_group("name", "description")

To create a subcommand, use the :meth:`.SlashCommandGroup.command` decorator.

.. code-block:: python3

    @foo.command()
    async def bar(ctx):  # this will show up as "/foo bar"

Slash command groups can also be created by subclassing :class:`.SlashCommandGroup`.

.. code-block:: python3

    from discord import SlashCommandGroup, slash_command

    class Foo(SlashCommandGroup):
        @slash_command()
        async def bar(self, ctx):
            ...

    bot.add_application_command(Foo())

    # or

    @bot.slash_group()
    class foo(SlashCommandGroup):
        @slash_command()
        async def bar(self, ctx):
            ...

Using Cogs
----------
