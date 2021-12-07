.. _discord_ext_menus:

``discord.ext.menus`` -- An extension module to provide useful menu options
===========================================================================

.. versionadded:: 2.0

Menus provide a easy pagination system with buttons

Example:
--------
A Basic Example Of `ext.menus` Being Used

.. code-block:: python3

    import discord
    from discord.commands import slash_command
    from discord.ext import commands, menus


    class MenusExample(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

            self.pages = [
                "Page One",
                discord.Embed(title="Page Two"),
                discord.Embed(title="Page Three"),
            ]
            self.pages[1].set_image(url="https://c.tenor.com/pPKOYQpTO8AAAAAM/monkey-developer.gif")
            self.pages[2].add_field(name="Example Field", value="Example Value", inline=False)
            self.pages[2].add_field(name="Another Example Field", value="Another Example Value", inline=False)

        def get_pages(self):
            return self.pages

        @slash_command(name="pageexample")
        async def pageexample(self, ctx):
            await ctx.defer()
            pages = menus.Paginator(pages=self.get_pages(), show_disabled=False, show_indicator=True)
            pages.customize_button("next", button_label=">", button_style=discord.ButtonStyle.green)
            pages.customize_button("prev", button_label="<", button_style=discord.ButtonStyle.green)
            pages.customize_button("first", button_label="<<", button_style=discord.ButtonStyle.blurple)
            pages.customize_button("last", button_label=">>", button_style=discord.ButtonStyle.blurple)
            await pages.send(ctx, ephemeral=False)

        @slash_command(name="pageexample_custom")
        async def pageexample_custom(self, ctx):
            await ctx.defer()
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Test Button, Does Nothing", row=1))
            view.add_item(
                discord.ui.Select(
                    placeholder="Test Select Menu, Does Nothing",
                    options=[discord.SelectOption(label="Example Option", value="Example Value", description="This menu does nothing!")],
                )
            )
            pages = menus.Paginator(pages=self.get_pages(), show_disabled=False, show_indicator=True, custom_view=view)
            await pages.send(ctx, ephemeral=False)


    def setup(bot):
        bot.add_cog(MenusExample(bot))

.. _discord_ext_menus_api:

API Reference
-------------

.. attributetable:: discord.ext.menus.Paginator

.. autoclass:: discord.ext.menus.Paginator
    :members: