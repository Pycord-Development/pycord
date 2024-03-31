.. _discord_ext_tasks:

discord.ext.tasks
=================

.. versionadded:: 1.1.0

One of the most common operations when making a bot is having a loop run in the background at a specified interval. This pattern is very common but has a lot of things you need to look out for:

- How do I handle :exc:`asyncio.CancelledError`?
- What do I do if the internet goes out?
- What is the maximum number of seconds I can sleep anyway?

The goal of this Pycord extension is to abstract all these worries away from you.

Recipes
-------

A simple background task in a :class:`~discord.ext.commands.Cog`:

.. code-block:: python3

    from discord.ext import tasks, commands

    class MyCog(commands.Cog):
        def __init__(self):
            self.index = 0
            self.printer.start()

        def cog_unload(self):
            self.printer.cancel()

        @tasks.loop(seconds=5.0)
        async def printer(self):
            print(self.index)
            self.index += 1

Adding an exception to handle during reconnect:

.. code-block:: python3

    import asyncpg
    from discord.ext import tasks, commands

    class MyCog(commands.Cog):
        def __init__(self, bot):
            self.bot = bot
            self.data = []
            self.batch_update.add_exception_type(asyncpg.PostgresConnectionError)
            self.batch_update.start()

        def cog_unload(self):
            self.batch_update.cancel()

        @tasks.loop(minutes=5.0)
        async def batch_update(self):
            async with self.bot.pool.acquire() as con:
                # batch update here...
                pass

Looping a certain amount of times before exiting:

.. code-block:: python3

    from discord.ext import tasks

    @tasks.loop(seconds=5.0, count=5)
    async def slow_count():
        print(slow_count.current_loop)

    @slow_count.after_loop
    async def after_slow_count():
        print('done!')

    slow_count.start()

Waiting until the bot is ready before the loop starts:

.. code-block:: python3

    from discord.ext import tasks, commands

    class MyCog(commands.Cog):
        def __init__(self, bot):
            self.index = 0
            self.bot = bot
            self.printer.start()

        def cog_unload(self):
            self.printer.cancel()

        @tasks.loop(seconds=5.0)
        async def printer(self):
            print(self.index)
            self.index += 1

        @printer.before_loop
        async def before_printer(self):
            print('waiting...')
            await self.bot.wait_until_ready()

Doing something during cancellation:

.. code-block:: python3

    from discord.ext import tasks, commands
    import asyncio

    class MyCog(commands.Cog):
        def __init__(self, bot):
            self.bot= bot
            self._batch = []
            self.lock = asyncio.Lock()
            self.bulker.start()

        async def do_bulk(self):
            # bulk insert data here
            ...

        @tasks.loop(seconds=10.0)
        async def bulker(self):
            async with self.lock:
                await self.do_bulk()

        @bulker.after_loop
        async def on_bulker_cancel(self):
            if self.bulker.is_being_cancelled() and len(self._batch) != 0:
                # if we're cancelled and we have some data left...
                # let's insert it to our database
                await self.do_bulk()


.. _ext_tasks_api:

API Reference
-------------

.. attributetable:: discord.ext.tasks.Loop

.. autoclass:: discord.ext.tasks.Loop()
    :members:
    :special-members: __call__
    :exclude-members: after_loop, before_loop, error

    .. automethod:: Loop.after_loop()
        :decorator:

    .. automethod:: Loop.before_loop()
        :decorator:

    .. automethod:: Loop.error()
        :decorator:

.. autofunction:: discord.ext.tasks.loop
