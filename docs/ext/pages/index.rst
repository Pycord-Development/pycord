.. _discord_ext_pages:

``discord.ext.pages`` -- An extension module to provide useful pagination options
===========================================================================

.. versionadded:: 2.0

This module provides an easy pagination system with buttons.

Example usage in a cog:

.. code-block:: python3

    import discord
    from discord.commands import slash_command
    from discord.ext import commands, pages


    class PageTest(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

            self.pages = [
                "Page One",  # string (text)
                discord.Embed(title="Page Two"),  # rich embed
                discord.Embed(title="Page Three"),  # another rich embed
            ]
            self.pages[1].set_image(url="https://c.tenor.com/pPKOYQpTO8AAAAAM/monkey-developer.gif")
            self.pages[2].add_field(name="Example Field", value="Example Value", inline=False)
            self.pages[2].add_field(name="Another Example Field", value="Another Example Value", inline=False)

        def get_pages(self):
            return self.pages

        @slash_command(name="pagetest")
        async def pagetest(self, ctx):
            await ctx.defer()
            # initializing the paginator
            paginator = pages.Paginator(pages=self.get_pages(), show_disabled=False, show_indicator=True)

            # customising buttons
            paginator.customize_button("next", button_label=">", button_style=discord.ButtonStyle.green)
            paginator.customize_button("prev", button_label="<", button_style=discord.ButtonStyle.green)
            paginator.customize_button("first", button_label="<<", button_style=discord.ButtonStyle.blurple)
            paginator.customize_button("last", button_label=">>", button_style=discord.ButtonStyle.blurple)

            # start paginating
            await paginator.send(ctx, ephemeral=False)

        # using a custom view
        @slash_command(name="pagetest_custom")
        async def pagetest_custom(self, ctx):
            await ctx.defer()
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Test Button, Does Nothing", row=1))
            view.add_item(
                discord.ui.Select(
                    placeholder="Test Select Menu, Does Nothing",
                    options=[discord.SelectOption(label="Example Option", value="Example Value", description="This menu does nothing!")],
                )
            )
            paginator = pages.Paginator(pages=self.get_pages(), show_disabled=False, show_indicator=True, custom_view=view)
            await paginator.send(ctx, ephemeral=False)


    def setup(bot):
        bot.add_cog(PageTest(bot))

.. _discord_ext_pages_api:

API Reference
-------------

.. attributetable:: discord.ext.pages.Paginator

.. autoclass:: discord.ext.pages.Paginator
    :members:

.. autoclass:: discord.ext.pages.PaginatorButton
    :members:
