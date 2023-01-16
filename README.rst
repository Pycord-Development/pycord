Pycord
======

.. image:: https://img.shields.io/discord/881207955029110855?label=discord&style=for-the-badge&logo=discord&color=5865F2&logoColor=white
   :target: https://pycord.dev/discord
   :alt: Discord server invite
.. image:: https://img.shields.io/pypi/v/py-cord.svg?style=for-the-badge&logo=pypi&color=yellowgreen&logoColor=white
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/py-cord.svg?style=for-the-badge&logo=python&logoColor=white
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPI supported Python versions
.. image:: https://img.shields.io/pypi/dm/py-cord?color=blueviolet&logo=pypi&logoColor=white&style=for-the-badge
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPI downloads
.. image:: https://img.shields.io/github/v/release/Pycord-Development/pycord?include_prereleases&label=Latest%20Release&logo=github&sort=semver&style=for-the-badge&logoColor=white
   :target: https://github.com/Pycord-Development/pycord/releases
   :alt: Latest release

A fork of discord.py. Pycord is a modern, easy to use, feature-rich, and async ready API wrapper for Discord written in Python.

Key Features
------------

- Modern Pythonic API using ``async`` and ``await``.
- Proper rate limit handling.
- Optimised for both speed and memory usage.
- Full Application Command Support

Installing
----------

**Python 3.8 or higher is required**

To install the library without full voice support, run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U py-cord

    # Windows
    py -3 -m pip install -U py-cord

Otherwise, to get full voice support, run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "py-cord[voice]"

    # Windows
    py -3 -m pip install -U py-cord[voice]

To install additional packages for speedup, run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "py-cord[speed]"
    # Windows
    py -3 -m pip install -U py-cord[speed]


To install the development version, do the following:

.. code:: sh

    $ git clone https://github.com/Pycord-Development/pycord
    $ cd pycord
    $ python3 -m pip install -U .[voice]

or if you do not want to clone the repository:

.. code:: sh

    # Linux/macOS
    python3 -m pip install git+https://github.com/Pycord-Development/pycord
    # Windows
    py -3 -m pip install git+https://github.com/Pycord-Development/pycord


Optional Packages
~~~~~~~~~~~~~~~~~

* `PyNaCl <https://pypi.org/project/PyNaCl/>`__ (for voice support)
* `aiodns <https://pypi.org/project/aiodns/>`__, `brotlipy <https://pypi.org/project/brotlipy/>`__, `cchardet <https://pypi.org/project/cchardet/>`__ (for aiohttp speedup)
* `orjson <https://pypi.org/project/orjson/>`__ (for json speedup)

Please note that while installing voice support on Linux, you must install the following packages via your preferred package manager (e.g. ``apt``, ``dnf``, etc) BEFORE running the above commands:

* libffi-dev (or ``libffi-devel`` on some systems)
* python-dev (e.g. ``python3.10-dev`` for Python 3.10)

Quick Example
-------------

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

Traditional Commands Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: py

    import discord
    from discord.ext import commands

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=">", intents=intents)

    @bot.command()
    async def ping(ctx):
        await ctx.send("pong")

    bot.run("token")

You can find more code examples in the ``examples`` directory.

Note: Make sure you do not reveal your bot token to anyone, as it can grant access to your bot.

Useful Links
------------

- `Documentation <https://docs.pycord.dev/en/master/index.html>`_
- `Learn how to create Discord bots with Pycord <https://guide.pycord.dev>`_
- `Our Official Discord Server <https://pycord.dev/discord>`_
- `Official Discord Developers Server <https://discord.gg/discord-developers>`_
