.. currentmodule:: discord.ext.ipc

Working with the `Session`
===========================
The :class:`Session` send requests for data and receives the data given back from the :class:`Server`.

Receiving data
--------------
To receive data you will want to use :meth:`Session.request`, like so:

.. code-block:: py

    from discord.ext import ipc
    from sanic import sanic

    app = Sanic(__name__)
    session = ipc.Session(...)

    @app.route("/")
    async def get_guild_categories():
        r = await session.request("give_guild_categories", guild_id=881207955029110855)
        print(r)

and vice versa for any other request being sent.