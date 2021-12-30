# Docs: https://docs.pycord.dev/en/master/ext/pages/index.html
# Note that the below examples use a Slash Command Group in a cog for better organization - it's not required for using ext.pages.

import discord
from discord.commands import SlashCommandGroup, slash_command
from discord.ext import commands, pages


class PageTest(commands.Cog):
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

    pagetest = SlashCommandGroup("pagetest", "Commands for testing ext.pages")

    @pagetest.command(name="default")
    async def pagetest_default(self, ctx: discord.ApplicationContext):
        """Demonstrates using the paginator with the default options."""
        paginator = pages.Paginator(pages=self.get_pages())
        await paginator.send(ctx, ephemeral=False)

    @pagetest.command(name="loop")
    async def pagetest_loop(self, ctx: discord.ApplicationContext):
        """Demonstrates using the loop_pages option."""
        paginator = pages.Paginator(pages=self.get_pages(), loop_pages=True)
        await paginator.send(ctx, ephemeral=False)

    @pagetest.command(name="strings")
    async def pagetest_strings(self, ctx: discord.ApplicationContext):
        """Demonstrates passing a list of strings as pages."""
        paginator = pages.Paginator(pages=["Page 1", "Page 2", "Page 3"], loop_pages=True)
        await paginator.send(ctx, ephemeral=False)

    @pagetest.command(name="timeout")
    async def pagetest_timeout(self, ctx: discord.ApplicationContext):
        """Demonstrates having the buttons be disabled when the paginator view times out."""
        paginator = pages.Paginator(pages=self.get_pages(), disable_on_timeout=True, timeout=30)
        await paginator.send(ctx, ephemeral=False)

    @pagetest.command(name="remove_buttons")
    async def pagetest_remove(self, ctx: discord.ApplicationContext):
        """Demonstrates using the default buttons, but removing some of them."""
        paginator = pages.Paginator(pages=self.get_pages())
        paginator.remove_button("first")
        paginator.remove_button("last")
        await paginator.send(ctx, ephemeral=False)

    @pagetest.command(name="init")
    async def pagetest_init(self, ctx: discord.ApplicationContext):
        """Demonstrates how to pass a list of custom buttons when creating the Paginator instance."""
        pagelist = [
            pages.PaginatorButton("first", label="<<-", style=discord.ButtonStyle.green),
            pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
            pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
            pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
            pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
        ]
        paginator = pages.Paginator(pages=self.get_pages(), show_disabled=True, show_indicator=True, use_default_buttons=False, custom_buttons=pagelist)
        await paginator.send(ctx, ephemeral=False)

    @pagetest.command(name="custom_buttons")
    async def pagetest_custom_buttons(self, ctx: discord.ApplicationContext):
        """Demonstrates adding buttons to the paginator when the default buttons are not used."""
        paginator = pages.Paginator(pages=self.get_pages(), use_default_buttons=False)
        paginator.add_button(pages.PaginatorButton("prev", label="<", style=discord.ButtonStyle.green))
        paginator.add_button(pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True))
        paginator.add_button(pages.PaginatorButton("next", style=discord.ButtonStyle.green))
        await paginator.send(ctx, ephemeral=False)

    @pagetest.command(name="custom_view")
    async def pagetest_custom_view(self, ctx: discord.ApplicationContext):
        """Demonstrates passing a custom view to the paginator."""
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Test Button, Does Nothing", row=1))
        view.add_item(
            discord.ui.Select(
                placeholder="Test Select Menu, Does Nothing",
                options=[discord.SelectOption(label="Example Option", value="Example Value", description="This menu does nothing!")],
            )
        )
        paginator = pages.Paginator(pages=self.get_pages(), custom_view=view)
        await paginator.send(ctx, ephemeral=False)


def setup(bot):
    bot.add_cog(PageTest(bot))