"""
The MIT License (MIT)

Copyright (c) 2021-present Pycord Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from typing import Dict, List, Optional, Union

import discord
from discord import abc
from discord.commands import ApplicationContext
from discord.ext.commands import Context


class PaginatorButton(discord.ui.Button):
    """Creates a button used to navigate the paginator.

    Parameters
    ----------
    button_type: :class:`str`
        The type of button being created.
        Must be one of ``first``, ``prev``, ``next``, or ``last``.
    paginator: :class:`Paginator`
        The paginator class where this button will be used.
    """

    def __init__(self, label, emoji, style, disabled, button_type, paginator):
        super().__init__(label=label, emoji=emoji, style=style, disabled=disabled, row=0)
        self.label = label
        self.emoji = emoji
        self.style = style
        self.disabled = disabled
        self.button_type = button_type
        self.paginator = paginator

    async def callback(self, interaction: discord.Interaction):
        if self.button_type == "first":
            self.paginator.current_page = 0
        elif self.button_type == "prev":
            self.paginator.current_page -= 1
        elif self.button_type == "next":
            self.paginator.current_page += 1
        elif self.button_type == "last":
            self.paginator.current_page = self.paginator.page_count
        await self.paginator.goto_page(interaction=interaction, page_number=self.paginator.current_page)


class Paginator(discord.ui.View):
    """Creates a paginator which can be sent as a message and uses buttons for navigation.

    Parameters
    ----------
    pages: Union[List[:class:`str`], List[:class:`discord.Embed`]]
        The list of strings and/or embeds to paginate.
    show_disabled: :class:`bool`
        Whether to show disabled buttons.
    show_indicator: :class:`bool`
        Whether to show the page indicator.
    author_check: :class:`bool`
        Whether only the original user of the command can change pages.
    disable_on_timeout: :class:`bool`
        Whether the buttons get disabled when the paginator view times out.
    custom_view: Optional[:class:`discord.ui.View`]
        A custom view whose items are appended below the pagination buttons.
    timeout: Optional[:class:`float`]
        Timeout in seconds from last interaction with the paginator before no longer accepting input. 

    Attributes
    ----------
    current_page: :class:`int`
        A zero-indexed value showing the current page number.
    page_count: :class:`int`
        A zero-indexed value showing the total number of pages.
    buttons: Dict[:class:`str`, Dict[:class:`str`, Union[:class:`~PaginatorButton`, :class:`bool`]]]
        A dictionary containing the :class:`~PaginatorButton` objects included in this paginator.
    user: Optional[Union[:class:`~discord.User`, :class:`~discord.Member`]]
        The user or member that invoked the paginator.
    message: Union[:class:`~discord.Message`, :class:`~discord.WebhookMessage`]
        The message the paginator is attached to.
    """

    def __init__(
        self,
        pages: Union[List[str], List[discord.Embed]],
        show_disabled=True,
        show_indicator=True,
        author_check=True,
        disable_on_timeout=True,
        custom_view: Optional[discord.ui.View] = None,
        timeout: Optional[float] = 180.0,
    ) -> None:
        super().__init__(timeout=timeout)
        self.timeout = timeout
        self.pages = pages
        self.current_page = 0
        self.page_count = len(self.pages) - 1
        self.show_disabled = show_disabled
        self.show_indicator = show_indicator
        self.disable_on_timeout = disable_on_timeout
        self.custom_view = custom_view
        self.message: Union[discord.Message, discord.WebhookMessage, None] = None
        self.buttons = {
            "first": {
                "object": PaginatorButton(
                    label="<<",
                    style=discord.ButtonStyle.blurple,
                    emoji=None,
                    disabled=True,
                    button_type="first",
                    paginator=self,
                ),
                "hidden": True,
            },
            "prev": {
                "object": PaginatorButton(
                    label="<",
                    style=discord.ButtonStyle.red,
                    emoji=None,
                    disabled=True,
                    button_type="prev",
                    paginator=self,
                ),
                "hidden": True,
            },
            "page_indicator": {
                "object": discord.ui.Button(
                    label=f"{self.current_page + 1}/{self.page_count + 1}",
                    style=discord.ButtonStyle.gray,
                    disabled=True,
                    row=0,
                ),
                "hidden": False,
            },
            "next": {
                "object": PaginatorButton(
                    label=">",
                    style=discord.ButtonStyle.green,
                    emoji=None,
                    disabled=True,
                    button_type="next",
                    paginator=self,
                ),
                "hidden": True,
            },
            "last": {
                "object": PaginatorButton(
                    label=">>",
                    style=discord.ButtonStyle.blurple,
                    emoji=None,
                    disabled=True,
                    button_type="last",
                    paginator=self,
                ),
                "hidden": True,
            },
        }
        self.update_buttons()

        self.usercheck = author_check
        self.user = None

    async def on_timeout(self) -> None:
        """Disables all buttons when the view times out."""
        if self.disable_on_timeout:
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)

    async def goto_page(self, interaction: discord.Interaction, page_number=0) -> None:
        """Updates the interaction response message to show the specified page number.

        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            The interaction that invoked the paginator.
        page_number: :class:`int`
            The page to display.

            .. note::

                Page numbers are zero-indexed when referenced internally, but appear as one-indexed when shown to the user.
        """
        self.update_buttons()
        page = self.pages[page_number]
        await interaction.response.edit_message(
            content=page if isinstance(page, str) else None, embed=page if isinstance(page, discord.Embed) else None, view=self
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.usercheck:
            return self.user == interaction.user
        return True

    def customize_button(
        self, button_name: str = None, button_label: str = None, button_emoji=None, button_style: discord.ButtonStyle = discord.ButtonStyle.gray
    ) -> PaginatorButton:
        """Allows you to easily customize the various pagination buttons.

        Parameters
        ----------
        button_name: :class:`str`
            The name of the button to customize.
            Must be one of ``first``, ``prev``, ``next``, or ``last``.
        button_label: :class:`str`
            The label to display on the button.
        button_emoji:
            The emoji to display on the button.
        button_style: :class:`~discord.ButtonStyle`
            The ButtonStyle to use for the button.

        Returns
        -------
        :class:`~PaginatorButton`
            The button that was customized.
        """

        if button_name not in self.buttons.keys():
            raise ValueError(f"no button named {button_name} was found in this view.")
        button: PaginatorButton = self.buttons[button_name]["object"]
        button.label = button_label
        button.emoji = button_emoji
        button.style = button_style
        return button

    def update_buttons(self) -> Dict:
        """Updates the display state of the buttons (disabled/hidden)

        Returns
        -------
        Dict[:class:`str`, Dict[:class:`str`, Union[:class:`~PaginatorButton`, :class:`bool`]]]
            The dictionary of buttons that were updated.
        """
        for key, button in self.buttons.items():
            if key == "first":
                if self.current_page <= 1:
                    button["hidden"] = True
                elif self.current_page >= 1:
                    button["hidden"] = False
            elif key == "last":
                if self.current_page >= self.page_count - 1:
                    button["hidden"] = True
                if self.current_page < self.page_count - 1:
                    button["hidden"] = False
            elif key == "next":
                if self.current_page == self.page_count:
                    button["hidden"] = True
                elif self.current_page < self.page_count:
                    button["hidden"] = False
            elif key == "prev":
                if self.current_page <= 0:
                    button["hidden"] = True
                elif self.current_page >= 0:
                    button["hidden"] = False
        self.clear_items()
        if self.show_indicator:
            self.buttons["page_indicator"]["object"].label = f"{self.current_page + 1}/{self.page_count + 1}"
        for key, button in self.buttons.items():
            if key != "page_indicator":
                if button["hidden"]:
                    button["object"].disabled = True
                    if self.show_disabled:
                        self.add_item(button["object"])
                else:
                    button["object"].disabled = False
                    self.add_item(button["object"])
            elif self.show_indicator:
                self.add_item(button["object"])

        # We're done adding standard buttons, so we can now add any specified custom view items below them
        # The bot developer should handle row assignments for their view before passing it to Paginator
        if self.custom_view:
            for item in self.custom_view.children:
                self.add_item(item)

        return self.buttons

    async def send(self, ctx: Union[ApplicationContext, Context], ephemeral: bool = False) -> Union[discord.Message, discord.WebhookMessage]:
        """Sends a message with the paginated items.


        Parameters
        ------------
        ctx: Union[:class:`~discord.ext.commands.Context`, :class:`~discord.ApplicationContext`]
            A command's invocation context.
        ephemeral: :class:`bool`
            Choose whether the message is ephemeral or not. Only works with slash commands.

        Returns
        --------
        Union[:class:`~discord.Message`, :class:`~discord.WebhookMessage`]
            The message that was sent with the paginator.
        """

        page = self.pages[0]

        self.user = ctx.author

        if isinstance(ctx, ApplicationContext):
            msg = await ctx.respond(
                content=page if isinstance(page, str) else None,
                embed=page if isinstance(page, discord.Embed) else None,
                view=self,
                ephemeral=ephemeral,
            )

        else:
            msg = await ctx.send(
                content=page if isinstance(page, str) else None,
                embed=page if isinstance(page, discord.Embed) else None,
                view=self,
            )
        if isinstance(msg, (discord.WebhookMessage, discord.Message)):
            self.message = msg
        elif isinstance(msg, discord.Interaction):
            self.message = await msg.original_message()

        return self.message

    async def respond(self, interaction: discord.Interaction, ephemeral: bool = False):
        """Sends an interaction response or followup with the paginated items.


        Parameters
        ------------
        interaction: :class:`discord.Interaction`
            The interaction associated with this response.
        ephemeral: :class:`bool`
            Choose whether the message is ephemeral or not.

        Returns
        --------
        :class:`~discord.Interaction`
            The message sent with the paginator.
        """
        page = self.pages[0]
        self.user = interaction.user

        if interaction.response.is_done():
            msg = await interaction.followup.send(
                content=page if isinstance(page, str) else None, embed=page if isinstance(page, discord.Embed) else None, view=self, ephemeral=ephemeral
            )

        else:
            msg = await interaction.response.send_message(
                content=page if isinstance(page, str) else None, embed=page if isinstance(page, discord.Embed) else None, view=self, ephemeral=ephemeral
            )
        if isinstance(msg, (discord.WebhookMessage, discord.Message)):
            self.message = msg
        elif isinstance(msg, discord.Interaction):
            self.message = await msg.original_message()
        return self.message

    async def update(
        self,
        interaction: discord.Interaction,
        pages: List[Union[str, discord.Embed]],
        show_disabled: Optional[bool] = None,
        show_indicator: Optional[bool] = None,
        author_check: Optional[bool] = None,
        disable_on_timeout: Optional[bool] = None,
        custom_view: Optional[discord.ui.View] = None,
        timeout: Optional[float] = None
    ):
        """Updates the paginator. This might be useful if you use a view with :class:`discord.SelectOption`
        and you have a different amount of pages depending on the selected option.

        Parameters
        ----------
        pages: List[Union[:class:`str`, :class:`discord.Embed`]]
            The list of strings and/or embeds to paginate.
        show_disabled: Optional[:class:`bool`]
            Whether to show disabled buttons.
        show_indicator: Optional[:class:`bool`]
            Whether to show the page indicator.
        author_check: Optional[:class:`bool`]
            Whether only the original user of the command can change pages.
        disable_on_timeout: Optional[:class:`bool`]
            Whether the buttons get disabled when the paginator view times out.
        custom_view: Optional[:class:`discord.ui.View`]
            A custom view whose items are appended below the pagination buttons.
        timeout: Optional[:class:`float`]
            Timeout in seconds from last interaction with the paginator before no longer accepting input. 
        """

        # Update pages and reset current_page to 0 (default)
        self.pages = pages
        self.page_count = len(self.pages) - 1
        self.current_page = 0
        # Apply config changes, if specified
        self.show_disabled = show_disabled if show_disabled else self.show_disabled
        self.show_indicator = show_indicator if show_indicator else self.show_indicator
        self.usercheck = author_check if author_check else self.usercheck
        self.disable_on_timeout = disable_on_timeout if disable_on_timeout else self.disable_on_timeout
        self.custom_view = custom_view if custom_view else self.custom_view
        self.timeout = timeout if timeout else self.timeout

        await self.goto_page(interaction, self.current_page)
