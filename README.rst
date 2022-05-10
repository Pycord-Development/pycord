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
Ответвление discord.py. Pycord - это современный, простой, богатый по функционалу, асинхронный инструмент для работы с Discord API, который написан на Python.

Основные преимущества:
------------

- Современное использование ``async`` и ``await``.
- Правильная работа с рейт лимитами.
- Оптимизирован для скорости и использовании памяти.
- Полная поддержка любых команд.

Установка
----------

**Требуется Python 3.8 или выше**

Чтобы установить библиотеку без полной поддержки голосового чата, вы можете просто запустить следующую команду:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U py-cord

    # Windows
    py -3 -m pip install -U py-cord

Чтобы получить поддержку голосового чата вы должны запустить следующую команду:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "py-cord[voice]"

    # Windows
    py -3 -m pip install -U py-cord[voice]

Чтобы установить дополнительные пакеты для ускорения, запустите следующую команду:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "py-cord[speed]"
    # Windows
    py -3 -m pip install -U py-cord[speed]


Чтобы установить разрабатываемую версию, запустите следующие команды:

.. code:: sh

    $ git clone https://github.com/Pycord-Development/pycord
    $ cd pycord
    $ python3 -m pip install -U .[voice]
    
Или если вы не хотите копировать репозиторий:

.. code:: sh

    # Linux/macOS
    python3 -m pip install git+https://github.com/Pycord-Development/pycord
    # Windows
    py -3 -m pip install git+https://github.com/Pycord-Development/pycord


Необязательные пакеты
~~~~~~~~~~~~~~~~~

* `PyNaCl <https://pypi.org/project/PyNaCl/>`__ (для поддержки голосового чата)
* `aiodns <https://pypi.org/project/aiodns/>`__, `brotlipy <https://pypi.org/project/brotlipy/>`__, `cchardet <https://pypi.org/project/cchardet/>`__ (для ускорения aiohttp)
* `orjson <https://pypi.org/project/orjson/>`__ (для ускорения json)

Примите во внимание, что если вы хотите использовать голосовой чат на Linux, вам необходимо установить следующие пакеты через ваш предпочтительный пакетный менеджер (например, ``apt``, ``dnf``, и т.д.) ДО запуска предыдущих команд:

* libffi-dev (or ``libffi-devel`` on some systems)
* python-dev (e.g. ``python3.10-dev`` for Python 3.10)

Быстрый пример
-------------

.. code:: py

    import discord

    bot = discord.Bot()

    @bot.slash_command()
    async def hello(ctx, name: str = None):
        name = name or ctx.author.name
        await ctx.respond(f"Привет, {name}!")

    @bot.user_command(name="Say Hello")
    async def hi(ctx, user):
        await ctx.respond(f"{ctx.author.mention} приветствует {user.name}!")

    bot.run("токен")

Традиционный пример команды
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: py

    import discord
    from discord.ext import commands

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=">", intents=intents)

    @bot.command()
    async def ping(ctx):
        await ctx.send("понг")

    bot.run("токен")

Вы можете найти больше примеров в папке "examples".

Заметка: Убедитесь, что вы никому не показываете токен вашего бота, он может предоставить полный доступ к вашему боту.

Полезные ссылки:
------------

- `Документация <https://docs.pycord.dev/en/master/index.html> разрабатывается русская`_
- `Учитесь тому, как создавать Дискорд ботов с Pycord <https://guide.pycord.dev> постараемся тоже перевести`_
- `Наш официальный дискорд сервер: <https://pycord.dev/discord>`_
- `Официальный дискорд сервер разработчиков Discord <https://discord.gg/discord-developers>`_
- `Неофициальный дискорд сервер Discord API <https://discord.gg/discord-api>`_
