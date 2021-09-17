pycord
==========

.. image:: https://img.shields.io/discord/881207955029110855?color=5865f2&label=Discord&logo=discord
   :target: https://discord.gg/dK2qkEJ37N
   :alt: Discord server invite
.. image:: https://img.shields.io/pypi/v/py-cord.svg
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/py-cord.svg
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPI supported Python versions

A fork of discord.py. PyCord is a modern, easy to use, feature-rich, and async ready API wrapper for Discord written in Python.

Key Features
-------------

- Modern Pythonic API using ``async`` and ``await``.
- Proper rate limit handling.
- Optimised for both speed and memory usage.

Installing
----------

**Python 3.8 or higher is required**

To install the library without full voice support, simply run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U py-cord

    # Windows
    py -3 -m pip install -U py-cord

Otherwise to get voice support you should run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "py-cord[voice]"

    # Windows
    py -3 -m pip install -U py-cord[voice]


To install the latest development version, do the following:

.. code:: sh

    $ git clone https://github.com/Pycord-Development/pycord
    $ cd pycord
    $ python3 -m pip install -U .[voice]


Optional Packages
~~~~~~~~~~~~~~~~~~

* `PyNaCl <https://pypi.org/project/PyNaCl/>`__ (for voice support)

Please note that while installing voice support on Linux, you must install the following packages via your preffered package manager (e.g. ``apt``, ``dnf``, etc) BEFORE running the above commands:

* libffi-dev (or ``libffi-devel`` on some systems)
* python-dev (e.g. ``python3.6-dev`` for Python 3.6)

Quick Example
--------------

.. code:: py

    import discord

    bot = discord.Bot()
    
    @bot.slash_command()
    async def hello(ctx, name: str = None):
        name = name or ctx.author.name
        await ctx.respond(f"Hello {name}!")
        
    @bot.user_command(name="Say Hello")
    async def hi(ctx, user):
        await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!")
        
    bot.run("token")

Normal Commands Example
~~~~~~~~~~~~~

.. code:: py

    import discord
    from discord.ext import commands

    bot = commands.Bot(command_prefix=">")

    @bot.command()
    async def ping(ctx):
        await ctx.send("pong")

    bot.run("token")

You can find more examples in the examples directory.

Note: Make sure you do not reveal your bot token to anyone, they could take control of it.

Links
------

- `Pycord Documentation <https://pycord.readthedocs.io/en/latest/index.html>`_
- `Pycord Discord Support Server <https://discord.gg/pycord>`_
- `Discord Developers Support Server <https://discord.gg/discord-developers>`_
- `Discord API Support Server <https://discord.gg/discord-api>`_
