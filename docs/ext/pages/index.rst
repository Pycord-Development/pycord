.. _discord_ext_pages:

``discord.ext.pages`` -- A pagination extension module
======================================================

.. versionadded:: 2.0

This module provides an easy pagination system with buttons, page groups, and custom view support.

Example usage in a cog:

.. code-block:: python3

    import asyncio

    import discord
    from discord.commands import SlashCommandGroup
    from discord.ext import commands, pages


    class PageTest(commands.Cog):
        def __init__(self, bot):
            self.bot = bot
            self.pages = [
                "Page 1",
                [
                    discord.Embed(title="Page 2, Embed 1"),
                    discord.Embed(title="Page 2, Embed 2"),
                ],
                "Page Three",
                discord.Embed(title="Page Four"),
                discord.Embed(title="Page Five"),
                [
                    discord.Embed(title="Page Six, Embed 1"),
                    discord.Embed(title="Page Seven, Embed 2"),
                ],
            ]
            self.pages[3].set_image(
                url="https://c.tenor.com/pPKOYQpTO8AAAAAM/monkey-developer.gif"
            )
            self.pages[4].add_field(
                name="Example Field", value="Example Value", inline=False
            )
            self.pages[4].add_field(
                name="Another Example Field", value="Another Example Value", inline=False
            )

            self.more_pages = [
                "Second Page One",
                discord.Embed(title="Second Page Two"),
                discord.Embed(title="Second Page Three"),
            ]

            self.even_more_pages = ["11111", "22222", "33333"]

        def get_pages(self):
            return self.pages

        pagetest = SlashCommandGroup("pagetest", "Commands for testing ext.pages")

        # These examples use a Slash Command Group in a cog for better organization - it's not required for using ext.pages.
        @pagetest.command(name="default")
        async def pagetest_default(self, ctx: discord.ApplicationContext):
            """Demonstrates using the paginator with the default options."""
            paginator = pages.Paginator(pages=self.get_pages())
            await paginator.respond(ctx.interaction, ephemeral=False)

        @pagetest.command(name="hidden")
        async def pagetest_hidden(self, ctx: discord.ApplicationContext):
            """Demonstrates using the paginator with disabled buttons hidden."""
            paginator = pages.Paginator(pages=self.get_pages(), show_disabled=False)
            await paginator.respond(ctx.interaction, ephemeral=False)

        @pagetest.command(name="loop")
        async def pagetest_loop(self, ctx: discord.ApplicationContext):
            """Demonstrates using the loop_pages option."""
            paginator = pages.Paginator(pages=self.get_pages(), loop_pages=True)
            await paginator.respond(ctx.interaction, ephemeral=False)

        @pagetest.command(name="strings")
        async def pagetest_strings(self, ctx: discord.ApplicationContext):
            """Demonstrates passing a list of strings as pages."""
            paginator = pages.Paginator(
                pages=["Page 1", "Page 2", "Page 3"], loop_pages=True
            )
            await paginator.respond(ctx.interaction, ephemeral=False)

        @pagetest.command(name="timeout")
        async def pagetest_timeout(self, ctx: discord.ApplicationContext):
            """Demonstrates having the buttons be disabled when the paginator view times out."""
            paginator = pages.Paginator(
                pages=self.get_pages(), disable_on_timeout=True, timeout=30
            )
            await paginator.respond(ctx.interaction, ephemeral=False)

        @pagetest.command(name="remove_buttons")
        async def pagetest_remove(self, ctx: discord.ApplicationContext):
            """Demonstrates using the default buttons, but removing some of them."""
            paginator = pages.Paginator(pages=self.get_pages())
            paginator.remove_button("first")
            paginator.remove_button("last")
            await paginator.respond(ctx.interaction, ephemeral=False)

        @pagetest.command(name="init")
        async def pagetest_init(self, ctx: discord.ApplicationContext):
            """Demonstrates how to pass a list of custom buttons when creating the Paginator instance."""
            pagelist = [
                pages.PaginatorButton(
                    "first", label="<<-", style=discord.ButtonStyle.green
                ),
                pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
                pages.PaginatorButton(
                    "page_indicator", style=discord.ButtonStyle.gray, disabled=True
                ),
                pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
                pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
            ]
            paginator = pages.Paginator(
                pages=self.get_pages(),
                show_disabled=True,
                show_indicator=True,
                use_default_buttons=False,
                custom_buttons=pagelist,
                loop_pages=True,
            )
            await paginator.respond(ctx.interaction, ephemeral=False)

        @pagetest.command(name="custom_buttons")
        async def pagetest_custom_buttons(self, ctx: discord.ApplicationContext):
            """Demonstrates adding buttons to the paginator when the default buttons are not used."""
            paginator = pages.Paginator(
                pages=self.get_pages(),
                use_default_buttons=False,
                loop_pages=False,
                show_disabled=False,
            )
            paginator.add_button(
                pages.PaginatorButton(
                    "prev", label="<", style=discord.ButtonStyle.green, loop_label="lst"
                )
            )
            paginator.add_button(
                pages.PaginatorButton(
                    "page_indicator", style=discord.ButtonStyle.gray, disabled=True
                )
            )
            paginator.add_button(
                pages.PaginatorButton(
                    "next", style=discord.ButtonStyle.green, loop_label="fst"
                )
            )
            await paginator.respond(ctx.interaction, ephemeral=False)

        @pagetest.command(name="custom_view")
        async def pagetest_custom_view(self, ctx: discord.ApplicationContext):
            """Demonstrates passing a custom view to the paginator."""
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Test Button, Does Nothing", row=1))
            view.add_item(
                discord.ui.Select(
                    placeholder="Test Select Menu, Does Nothing",
                    options=[
                        discord.SelectOption(
                            label="Example Option",
                            value="Example Value",
                            description="This menu does nothing!",
                        )
                    ],
                )
            )
            paginator = pages.Paginator(pages=self.get_pages(), custom_view=view)
            await paginator.respond(ctx.interaction, ephemeral=False)

        @pagetest.command(name="groups")
        async def pagetest_groups(self, ctx: discord.ApplicationContext):
            """Demonstrates using page groups to switch between different sets of pages."""
            page_buttons = [
                pages.PaginatorButton(
                    "first", label="<<-", style=discord.ButtonStyle.green
                ),
                pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
                pages.PaginatorButton(
                    "page_indicator", style=discord.ButtonStyle.gray, disabled=True
                ),
                pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
                pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
            ]
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Test Button, Does Nothing", row=2))
            view.add_item(
                discord.ui.Select(
                    placeholder="Test Select Menu, Does Nothing",
                    options=[
                        discord.SelectOption(
                            label="Example Option",
                            value="Example Value",
                            description="This menu does nothing!",
                        )
                    ],
                )
            )
            page_groups = [
                pages.PageGroup(
                    pages=self.get_pages(),
                    label="Main Page Group",
                    description="Main Pages for Main Things",
                ),
                pages.PageGroup(
                    pages=[
                        "Second Set of Pages, Page 1",
                        "Second Set of Pages, Page 2",
                        "Look, it's group 2, page 3!",
                    ],
                    label="Second Page Group",
                    description="Secondary Pages for Secondary Things",
                    custom_buttons=page_buttons,
                    use_default_buttons=False,
                    custom_view=view,
                ),
            ]
            paginator = pages.Paginator(pages=page_groups, show_menu=True)
            await paginator.respond(ctx.interaction, ephemeral=False)

        @pagetest.command(name="update")
        async def pagetest_update(self, ctx: discord.ApplicationContext):
            """Demonstrates updating an existing paginator instance with different options."""
            paginator = pages.Paginator(pages=self.get_pages(), show_disabled=False)
            await paginator.respond(ctx.interaction)
            await asyncio.sleep(3)
            await paginator.update(show_disabled=True, show_indicator=False)

        @pagetest.command(name="target")
        async def pagetest_target(self, ctx: discord.ApplicationContext):
            """Demonstrates sending the paginator to a different target than where it was invoked."""
            paginator = pages.Paginator(pages=self.get_pages())
            await paginator.respond(ctx.interaction, target=ctx.interaction.user)

        @commands.command()
        async def pagetest_prefix(self, ctx: commands.Context):
            """Demonstrates using the paginator with a prefix-based command."""
            paginator = pages.Paginator(pages=self.get_pages(), use_default_buttons=False)
            paginator.add_button(
                pages.PaginatorButton("prev", label="<", style=discord.ButtonStyle.green)
            )
            paginator.add_button(
                pages.PaginatorButton(
                    "page_indicator", style=discord.ButtonStyle.gray, disabled=True
                )
            )
            paginator.add_button(
                pages.PaginatorButton("next", style=discord.ButtonStyle.green)
            )
            await paginator.send(ctx)

        @commands.command()
        async def pagetest_target(self, ctx: commands.Context):
            """Demonstrates sending the paginator to a different target than where it was invoked (prefix-command version)."""
            paginator = pages.Paginator(pages=self.get_pages())
            await paginator.send(ctx, target=ctx.author, target_message="Paginator sent!")


    def setup(bot):
        bot.add_cog(PageTest(bot))

.. _discord_ext_pages_api:

API Reference
=============

Paginator
---------

.. attributetable:: discord.ext.pages.Paginator

.. autoclass:: discord.ext.pages.Paginator
    :members:
    :inherited-members:

PaginatorButton
---------------

.. attributetable:: discord.ext.pages.PaginatorButton

.. autoclass:: discord.ext.pages.PaginatorButton
    :members:
    :inherited-members:

PaginatorMenu
-------------

.. attributetable:: discord.ext.pages.PaginatorMenu

.. autoclass:: discord.ext.pages.PaginatorMenu
    :members:
    :inherited-members:

PageGroup
---------

.. attributetable:: discord.ext.pages.PageGroup

.. autoclass:: discord.ext.pages.PageGroup
    :members:
    :inherited-members:
