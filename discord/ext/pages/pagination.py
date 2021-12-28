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

__all__ = (
    "PaginatorButton",
    "Paginator",
)


class PaginatorButton(discord.ui.Button):
    """Creates a button used to navigate the paginator.

    Parameters
    ----------
    button_type: :class:`str`
        The type of button being created.
        Must be one of ``first``, ``prev``, ``next``, ``last``, or ``page_indicator``.
    label: :class:`str`
        The label shown on the button.
        Defaults to a capitalized version of `button_type` (e.g. "Next", "Prev", etc)
    emoji: Union[:class:`str`, :class:`discord.Emoji`, :class:`discord.PartialEmoji`]
        The emoji shown on the button in front of the label.
    disabled: :class:`bool`
        Whether to initially show the button as disabled.
    loop_label: :class:`str`
        The label shown on the button when ``loop_pages`` is set to ``True`` in the Paginator class.

    Attributes
    ----------
    paginator: :class:`Paginator`
        The paginator class where this button is being used.
        Assigned to the button when `Paginator.add_button` is called.
    """

    def __init__(
        self,
        button_type: str,
        label: str = None,
        emoji: Union[str, discord.Emoji, discord.PartialEmoji] = None,
        style: discord.ButtonStyle = discord.ButtonStyle.green,
        disabled: bool = False,
        custom_id: str = None,
        loop_label: str = None,
    ):
        super().__init__(
            label=label,
            emoji=emoji,
            style=style,
            disabled=disabled,
            custom_id=custom_id,
            row=0,
        )
        self.button_type = button_type
        self.label = label
        self.emoji = emoji
        self.style = style
        self.disabled = disabled
        self.loop_label = self.label if not loop_label else loop_label
        self.paginator = None

    async def callback(self, interaction: discord.Interaction):
        if self.button_type == "first":
            self.paginator.current_page = 0
        elif self.button_type == "prev":
            if self.paginator.loop_pages and self.paginator.current_page == 0:
                self.paginator.current_page = self.paginator.page_count
            else:
                self.paginator.current_page -= 1
        elif self.button_type == "next":
            if self.paginator.loop_pages and self.paginator.current_page == self.paginator.page_count:
                self.paginator.current_page = 0
            else:
                self.paginator.current_page += 1
        elif self.button_type == "last":
            self.paginator.current_page = self.paginator.page_count
        await self.paginator.goto_page(
            interaction=interaction, page_number=self.paginator.current_page
        )


class Paginator(discord.ui.View):
    """Creates a paginator which can be sent as a message and uses buttons for navigation.

    Parameters
    ----------
    pages: Union[List[:class:`str`], List[:class:`discord.Embed`]]
        The list of strings and/or embeds to paginate.
    show_disabled: :class:`bool`
        Whether to show disabled buttons.
    show_indicator: :class:`bool`
        Whether to show the page indicator when using the default buttons.
    author_check: :class:`bool`
        Whether only the original user of the command can change pages.
    disable_on_timeout: :class:`bool`
        Whether the buttons get disabled when the paginator view times out.
    use_default_buttons: :class:`bool`
        Whether to use the default buttons (i.e. ``first``, ``prev``, ``page_indicator``, ``next``, ``last``)
    loop_pages: :class:`bool`
        Whether to loop the pages when clicking prev/next while at the first/last page in the list.
    custom_buttons: Optional[List[:class:`PaginatorButton`]]
        A list of PaginatorButtons to initialize the Paginator with.
        If ``use_default_buttons`` is ``True``, this parameter is ignored.
    custom_view: Optional[:class:`discord.ui.View`]
        A custom view whose items are appended below the pagination buttons.


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
        use_default_buttons=True,
        loop_pages=False,
        custom_view: Optional[discord.ui.View] = None,
        timeout: Optional[float] = 180.0,
        custom_buttons: Optional[List[PaginatorButton]] = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self.timeout = timeout
        self.pages = pages
        self.current_page = 0
        self.page_count = len(self.pages) - 1
        self.buttons = {}
        self.show_disabled = show_disabled
        self.show_indicator = show_indicator
        self.disable_on_timeout = disable_on_timeout
        self.use_default_buttons = use_default_buttons
        self.loop_pages = loop_pages
        self.custom_view = custom_view
        self.message: Union[discord.Message, discord.WebhookMessage, None] = None
        if custom_buttons and not self.use_default_buttons:
            for button in custom_buttons:
                self.add_button(button)
        elif not custom_buttons and self.use_default_buttons:
            self.add_default_buttons()

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
            The interaction that invoked the Paginator
        page_number: :class:`int`
            The page to display.

            .. note::

                Page numbers are zero-indexed when referenced internally, but appear as one-indexed when shown to the user.
        """
        self.update_buttons()
        page = self.pages[page_number]
        await interaction.response.edit_message(
            content=page if isinstance(page, str) else None,
            embed=page if isinstance(page, discord.Embed) else None,
            view=self,
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.usercheck:
            return self.user == interaction.user
        return True

    def add_default_buttons(self):
        default_buttons = [
            PaginatorButton("first", label="<<", style=discord.ButtonStyle.blurple),
            PaginatorButton("prev", label="<", style=discord.ButtonStyle.red, loop_label="↪"),
            PaginatorButton(
                "page_indicator", style=discord.ButtonStyle.gray, disabled=True
            ),
            PaginatorButton("next", label=">", style=discord.ButtonStyle.green, loop_label="↩"),
            PaginatorButton("last", label=">>", style=discord.ButtonStyle.blurple),
        ]
        for button in default_buttons:
            self.add_button(button)

    def add_button(self, button: PaginatorButton):
        self.buttons[button.button_type] = {
            "object": discord.ui.Button(
                style=button.style,
                label=button.label or button.button_type.capitalize()
                if button.button_type != "page_indicator"
                else f"{self.current_page + 1}/{self.page_count + 1}",
                disabled=button.disabled,
                custom_id=button.custom_id,
                emoji=button.emoji,
                row=button.row,
            ),
            "loop_label": button.loop_label,
            "hidden": button.disabled
            if button.button_type != "page_indicator"
            else not self.show_indicator,
        }
        self.buttons[button.button_type]["object"].callback = button.callback
        button.paginator = self

    def remove_button(self, button_type: str):
        if button_type not in self.buttons.keys():
            raise ValueError(
                f"no button_type {button_type} was found in this paginator."
            )
        self.buttons.pop(button_type)

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
                    if not self.loop_pages:
                        button["hidden"] = True
                    else:
                        button["object"].label = button["loop_label"]
                elif self.current_page < self.page_count:
                    button["hidden"] = False
            elif key == "prev":
                if self.current_page <= 0:
                    if not self.loop_pages:
                        button["hidden"] = True
                    else:
                        button["object"].label = button["loop_label"]
                elif self.current_page >= 0:
                    button["hidden"] = False
        self.clear_items()
        if self.show_indicator:
            self.buttons["page_indicator"][
                "object"
            ].label = f"{self.current_page + 1}/{self.page_count + 1}"
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

    async def send(
        self,
        ctx: Union[ApplicationContext, Context],
        ephemeral: bool = False,
    ) -> Union[discord.Message, discord.WebhookMessage]:
        """Sends a message with the paginated items.


        Parameters
        ------------
        ctx: Union[:class:`~discord.ext.commands.Context`, :class:`~discord.ApplicationContext`]
            The invocation context.
        ephemeral: :class:`bool`
            Choose whether the message is ephemeral or not. Only works with slash commands.

        Returns
        --------
        Union[:class:`~discord.Message`, :class:`~discord.WebhookMessage`]
            The message that was sent with the paginator.
        """

        self.update_buttons()
        page = self.pages[0]

        self.user = ctx.author

        if isinstance(ctx, ApplicationContext):
            msg = await ctx.respond(
                content=page if isinstance(page, str) else None,
                embeds=[page] if isinstance(page, discord.Embed) else None,
                view=self,
                ephemeral=ephemeral,
            )

        else:
            msg = await ctx.send(
                content=page if isinstance(page, str) else None,
                embeds=[page] if isinstance(page, discord.Embed) else None,
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
        if not isinstance(interaction, discord.Interaction):
            raise TypeError(f"expected Interaction not {interaction.__class__!r}")
        self.update_buttons()

        page = self.pages[0]
        self.user = interaction.user

        if interaction.response.is_done():
            msg = await interaction.followup.send(
                content=page if isinstance(page, str) else None,
                embeds=[page] if isinstance(page, discord.Embed) else None,
                view=self,
                ephemeral=ephemeral,
            )

        else:
            msg = await interaction.response.send_message(
                content=page if isinstance(page, str) else None,
                embeds=[page] if isinstance(page, discord.Embed) else None,
                view=self,
                ephemeral=ephemeral,
            )
        if isinstance(msg, (discord.WebhookMessage, discord.Message)):
            self.message = msg
        elif isinstance(msg, discord.Interaction):
            self.message = await msg.original_message()
        return self.message
