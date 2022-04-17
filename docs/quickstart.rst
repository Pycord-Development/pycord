:orphan:

.. _quickstart:

.. currentmodule:: discord

Quickstart
==========

This page gives a brief introduction to the library. It assumes you have the library installed.
If you don't, check the :ref:`installing` portion.

A Minimal Bot
-------------

Let's make a bot that responds to a specific message and walk you through it.

It looks something like this:

.. note::

    Because this example utilizes message content, it requires the :attr:`Intents.message_content` privileged intent.

.. code-block:: python3

    import discord

    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

    client.run('your token here')

Let's name this file ``example_bot.py``. Make sure not to name it ``discord.py`` as that'll conflict
with the library.

There's a lot going on here, so let's walk you through it step by step:

1. The first line just imports the library, if this raises a `ModuleNotFoundError` or `ImportError`
   then head on over to :ref:`installing` section to properly install.
2. Next, we create an instance of a :class:`Client`. This client is our connection to Discord.
3. We then use the :meth:`Client.event` decorator to register an event. This library has many events.
   Since this library is asynchronous, we do things in a "callback" style manner.

   A callback is essentially a function that is called when something happens. In our case,
   the :func:`on_ready` event is called when the bot has finished logging in and setting things
   up and the :func:`on_message` event is called when the bot has received a message.
4. Since the :func:`on_message` event triggers for *every* message received, we have to make
   sure that we ignore messages from ourselves. We do this by checking if the :attr:`Message.author`
   is the same as the :attr:`Client.user`.
5. Afterwards, we check if the :class:`Message.content` starts with ``'$hello'``. If it does,
   then we send a message in the channel it was used in with ``'Hello!'``. This is a basic way of
   handling commands, which can be later automated with the :doc:`./ext/commands/index` framework.
6. Finally, we run the bot with our login token. If you need help getting your token or creating a bot,
   look in the :ref:`discord-intro` section.


Now that we've made a bot, we have to *run* the bot. Luckily, this is simple since this is just a
Python script, we can run it directly.

On Windows:

.. code-block:: shell

    $ py -3 example_bot.py

On other systems:

.. code-block:: shell

    $ python3 example_bot.py

Now you can try playing around with your basic bot.

A Minimal Bot with Slash Commands
---------------------------------

As a continuation, let's create a bot that registers a simple slash command!

It looks something like this:

.. code-block:: python3

    import discord

    bot = discord.Bot()

    @bot.event
    async def on_ready():
        print(f"We have logged in as {bot.user}")

    @bot.slash_command(guild_ids=[your, guild_ids, here])
    async def hello(ctx):
        await ctx.respond("Hello!")

    bot.run("your token here")

Let's look at the differences compared to the previous example, step-by-step:

1. The first line remains unchanged.
2. Next, we create an instance of :class:`.Bot`. This is different from :class:`.Client`, as it supports
   slash command creation and other features, while inheriting all the features of :class:`.Client`.
3. We then use the :meth:`.Bot.slash_command` decorator to register a new slash command.
   The ``guild_ids`` attribute contains a list of guilds where this command will be active.
   If you omit it, the command will be globally available, and may take up to an hour to register.
4. Afterwards, we trigger a response to the slash command in the form of a text reply. Please note that
   all slash commands must have some form of response, otherwise they will fail.
5. Finally, we, once again, run the bot with our login token.


Congratulations! Now you have created your first slash command!
