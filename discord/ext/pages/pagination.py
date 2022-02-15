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
from discord.ext.commands import Context

__all__ = (
    "PaginatorButton",
    "Paginator",
    "PageGroup",
    "PaginatorMenu",
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
        Defaults to a capitalized version of ``button_type`` (e.g. "Next", "Prev", etc.)
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
        Assigned to the button when ``Paginator.add_button`` is called.
    """

    def __init__(
        self,
        button_type: str,
        label: str = None,
        emoji: Union[str, discord.Emoji, discord.PartialEmoji] = None,
        style: discord.ButtonStyle = discord.ButtonStyle.green,
        disabled: bool = False,
        custom_id: str = None,
        row: int = 0,
        loop_label: str = None,
    ):
        super().__init__(
            label=label if label or emoji else button_type.capitalize(),
            emoji=emoji,
            style=style,
            disabled=disabled,
            custom_id=custom_id,
            row=row,
        )
        self.button_type = button_type
        self.label = label if label or emoji else button_type.capitalize()
        self.emoji: Union[str, discord.Emoji, discord.PartialEmoji] = emoji
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
        await self.paginator.goto_page(page_number=self.paginator.current_page)


class PageGroup:
    """Creates a group of pages which the user can switch between.

    Each group of pages can have its own options, custom buttons, custom views, etc.

    .. note::

        If multiple ``PageGroup`` objects have different options, they should all be set explicitly when creating each instance.


    Parameters
    ----------
    pages: Union[List[:class:`str`], List[Union[List[:class:`discord.Embed`], :class:`discord.Embed]]]
        The list of strings, embeds, or list of embeds to include in the page group.
    label: :class:`str`
        The label shown on the corresponding PaginatorMenu dropdown option.
        Also used as the SelectOption value.
    description: :class:`str`
        The description shown on the corresponding PaginatorMenu dropdown option.
    emoji: Union[:class:`str`, :class:`discord.Emoji`, :class:`discord.PartialEmoji`]
        The emoji shown on the corresponding PaginatorMenu dropdown option.
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
    default_button_row: :class:`int`
        The row where the default paginator buttons are displayed. Has no effect if custom buttons are used.
    loop_pages: :class:`bool`
        Whether to loop the pages when clicking prev/next while at the first/last page in the list.
    custom_view: Optional[:class:`discord.ui.View`]
        A custom view whose items are appended below the pagination buttons.
    timeout: Optional[:class:`float`]
        Timeout in seconds from last interaction with the paginator before no longer accepting input.
    custom_buttons: Optional[List[:class:`PaginatorButton`]]
        A list of PaginatorButtons to initialize the Paginator with.
        If ``use_default_buttons`` is ``True``, this parameter is ignored.
    """

    def __init__(
        self,
        pages: Union[List[str], List[Union[List[discord.Embed], discord.Embed]]],
        label: str,
        description: str,
        emoji: Union[str, discord.Emoji, discord.PartialEmoji] = None,
        show_disabled: Optional[bool] = None,
        show_indicator: Optional[bool] = None,
        author_check: Optional[bool] = None,
        disable_on_timeout: Optional[bool] = None,
        use_default_buttons: Optional[bool] = None,
        default_button_row: int = 0,
        loop_pages: Optional[bool] = None,
        custom_view: Optional[discord.ui.View] = None,
        timeout: Optional[float] = None,
        custom_buttons: Optional[List[PaginatorButton]] = None,
    ):
        self.label = label
        self.description = description
        self.emoji: Union[str, discord.Emoji, discord.PartialEmoji] = emoji
        self.pages: Union[List[str], List[Union[List[discord.Embed], discord.Embed]]] = pages
        self.show_disabled = show_disabled
        self.show_indicator = show_indicator
        self.author_check = author_check
        self.disable_on_timeout = disable_on_timeout
        self.use_default_buttons = use_default_buttons
        self.default_button_row = default_button_row
        self.loop_pages = loop_pages
        self.custom_view: discord.ui.View = custom_view
        self.timeout: float = timeout
        self.custom_buttons: List = custom_buttons


class Paginator(discord.ui.View):
    """Creates a paginator which can be sent as a message and uses buttons for navigation.

    Parameters
    ----------
    pages: Union[List[:class:`PageGroup`], List[:class:`str`], List[Union[List[:class:`discord.Embed`], :class:`discord.Embed`]]]
        The list of :class:`PageGroup` objects, strings, embeds, or list of embeds to paginate.
        If a list of :class:`PageGroup` objects is provided and `show_menu` is ``False``, only the first page group will be displayed.
    show_disabled: :class:`bool`
        Whether to show disabled buttons.
    show_indicator: :class:`bool`
        Whether to show the page indicator when using the default buttons.
    show_menu: :class:`bool`
        Whether to show a select menu that allows the user to switch between groups of pages.
    author_check: :class:`bool`
        Whether only the original user of the command can change pages.
    disable_on_timeout: :class:`bool`
        Whether the buttons get disabled when the paginator view times out.
    use_default_buttons: :class:`bool`
        Whether to use the default buttons (i.e. ``first``, ``prev``, ``page_indicator``, ``next``, ``last``)
    default_button_row: :class:`int`
        The row where the default paginator buttons are displayed. Has no effect if custom buttons are used.
    loop_pages: :class:`bool`
        Whether to loop the pages when clicking prev/next while at the first/last page in the list.
    custom_view: Optional[:class:`discord.ui.View`]
        A custom view whose items are appended below the pagination components.
    timeout: Optional[:class:`float`]
        Timeout in seconds from last interaction with the paginator before no longer accepting input.
    custom_buttons: Optional[List[:class:`PaginatorButton`]]
        A list of PaginatorButtons to initialize the Paginator with.
        If ``use_default_buttons`` is ``True``, this parameter is ignored.

    Attributes
    ----------
    menu: Optional[List[:class:`PaginatorMenu`]]
        The page group select menu associated with this paginator.
    page_groups: Optional[List[:class:`PageGroup`]]
        List of :class:`PageGroup` objects the user can switch between.
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
        pages: Union[List[PageGroup], List[str], List[Union[List[discord.Embed], discord.Embed]]],
        show_disabled: bool = True,
        show_indicator=True,
        show_menu=False,
        author_check=True,
        disable_on_timeout=True,
        use_default_buttons=True,
        default_button_row: int = 0,
        loop_pages=False,
        custom_view: Optional[discord.ui.View] = None,
        timeout: Optional[float] = 180.0,
        custom_buttons: Optional[List[PaginatorButton]] = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self.timeout: float = timeout
        self.pages: Union[List[PageGroup], List[str], List[Union[List[discord.Embed], discord.Embed]]] = pages
        self.current_page = 0
        self.menu: Optional[PaginatorMenu] = None
        self.show_menu = show_menu
        self.page_groups: Optional[List[PageGroup]] = None

        if all(isinstance(pg, PageGroup) for pg in pages):
            self.page_groups = self.pages if show_menu else None
            self.pages: Union[List[str], List[Union[List[discord.Embed], discord.Embed]]] = self.page_groups[0].pages

        self.page_count = len(self.pages) - 1
        self.buttons = {}
        self.custom_buttons: List = custom_buttons
        self.show_disabled = show_disabled
        self.show_indicator = show_indicator
        self.disable_on_timeout = disable_on_timeout
        self.use_default_buttons = use_default_buttons
        self.default_button_row = default_button_row
        self.loop_pages = loop_pages
        self.custom_view: discord.ui.View = custom_view
        self.message: Union[discord.Message, discord.WebhookMessage, None] = None

        if self.custom_buttons and not self.use_default_buttons:
            for button in custom_buttons:
                self.add_button(button)
        elif not self.custom_buttons and self.use_default_buttons:
            self.add_default_buttons()

        if self.show_menu:
            self.add_menu()

        self.usercheck = author_check
        self.user = None

    async def update(
        self,
        pages: Optional[Union[List[str], List[Union[List[discord.Embed], discord.Embed]]]] = None,
        show_disabled: Optional[bool] = None,
        show_indicator: Optional[bool] = None,
        author_check: Optional[bool] = None,
        disable_on_timeout: Optional[bool] = None,
        use_default_buttons: Optional[bool] = None,
        default_button_row: Optional[int] = None,
        loop_pages: Optional[bool] = None,
        custom_view: Optional[discord.ui.View] = None,
        timeout: Optional[float] = None,
        custom_buttons: Optional[List[PaginatorButton]] = None,
    ):
        """Updates the existing :class:`Paginator` instance with the provided options.

        Parameters
        ----------
        pages: Optional[Union[List[:class:`PageGroup`], List[:class:`str`], List[Union[List[:class:`discord.Embed`], :class:`discord.Embed]]]]
            The list of :class:`PageGroup` objects, strings, embeds, or list of embeds to paginate.
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
        default_button_row: Optional[:class:`int`]
            The row where the default paginator buttons are displayed. Has no effect if custom buttons are used.
        loop_pages: :class:`bool`
            Whether to loop the pages when clicking prev/next while at the first/last page in the list.
        custom_view: Optional[:class:`discord.ui.View`]
            A custom view whose items are appended below the pagination components.
        timeout: Optional[:class:`float`]
            Timeout in seconds from last interaction with the paginator before no longer accepting input.
        custom_buttons: Optional[List[:class:`PaginatorButton`]]
            A list of PaginatorButtons to initialize the Paginator with.
            If ``use_default_buttons`` is ``True``, this parameter is ignored.
        """

        # Update pages and reset current_page to 0 (default)
        self.pages: Union[List[PageGroup], List[str], List[Union[List[discord.Embed], discord.Embed]]] = (
            pages if pages is not None else self.pages
        )
        self.page_count = len(self.pages) - 1
        self.current_page = 0
        # Apply config changes, if specified
        self.show_disabled = show_disabled if show_disabled is not None else self.show_disabled
        self.show_indicator = show_indicator if show_indicator is not None else self.show_indicator
        self.usercheck = author_check if author_check is not None else self.usercheck
        self.disable_on_timeout = disable_on_timeout if disable_on_timeout is not None else self.disable_on_timeout
        self.use_default_buttons = use_default_buttons if use_default_buttons is not None else self.use_default_buttons
        self.default_button_row = default_button_row if default_button_row is not None else self.default_button_row
        self.loop_pages = loop_pages if loop_pages is not None else self.loop_pages
        self.custom_view: discord.ui.View = None if custom_view is None else custom_view
        self.timeout: float = timeout if timeout is not None else self.timeout
        if custom_buttons and not self.use_default_buttons:
            self.buttons = {}
            for button in custom_buttons:
                self.add_button(button)
        else:
            self.buttons = {}
            self.add_default_buttons()

        await self.goto_page(self.current_page)

    async def on_timeout(self) -> None:
        """Disables all buttons when the view times out."""
        if self.disable_on_timeout:
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)

    async def disable(
        self,
        include_custom: bool = False,
        page: Optional[Union[str, Union[List[discord.Embed], discord.Embed]]] = None,
    ) -> None:
        """Stops the paginator, disabling all of its components.

        Parameters
        ----------
        include_custom: :class:`bool`
            Whether to disable components added via custom views.
        page: Optional[Union[:class:`str`, Union[List[:class:`discord.Embed`], :class:`discord.Embed`]]]
            The page content to show after disabling the paginator.
        """
        page = self.get_page_content(page)
        for item in self.children:
            if item not in self.custom_view.children or include_custom:
                item.disabled = True
        if page:
            await self.message.edit(
                content=page if isinstance(page, str) else None,
                embeds=[] if isinstance(page, str) else page,
                view=self,
            )
        else:
            await self.message.edit(view=self)

    async def cancel(
        self,
        include_custom: bool = False,
        page: Optional[Union[str, Union[List[discord.Embed], discord.Embed]]] = None,
    ) -> None:
        """Cancels the paginator, removing all of its components from the message.

        Parameters
        ----------
        include_custom: :class:`bool`
            Whether to remove components added via custom views.
        page: Optional[Union[:class:`str`, Union[List[:class:`discord.Embed`], :class:`discord.Embed`]]]
            The page content to show after canceling the paginator.
        """
        items = self.children.copy()
        page = self.get_page_content(page)
        for item in items:
            if item not in self.custom_view.children or include_custom:
                self.remove_item(item)
        if page:
            await self.message.edit(
                content=page if isinstance(page, str) else None,
                embeds=[] if isinstance(page, str) else page,
                view=self,
            )
        else:
            await self.message.edit(view=self)

    async def goto_page(self, page_number=0) -> discord.Message:
        """Updates the paginator message to show the specified page number.

        Parameters
        ----------
        page_number: :class:`int`
            The page to display.

            .. note::

                Page numbers are zero-indexed when referenced internally, but appear as one-indexed when shown to the user.

        Returns
        -------
        :class:`~discord.Message`
            The message associated with the paginator.
        """
        self.update_buttons()
        self.current_page = page_number
        if self.show_indicator:
            self.buttons["page_indicator"]["object"].label = f"{self.current_page + 1}/{self.page_count + 1}"

        page = self.pages[page_number]
        page = self.get_page_content(page)

        return await self.message.edit(
            content=page if isinstance(page, str) else None,
            embeds=[] if isinstance(page, str) else page,
            view=self,
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.usercheck:
            return self.user == interaction.user
        return True

    def add_menu(self):
        """Adds the default :class:`PaginatorMenu` instance to the paginator."""
        self.menu = PaginatorMenu(self.page_groups)
        self.menu.paginator = self
        self.add_item(self.menu)

    def add_default_buttons(self):
        """Adds the full list of default buttons that can be used with the paginator.
        Includes ``first``, ``prev``, ``page_indicator``, ``next``, and ``last``."""
        default_buttons = [
            PaginatorButton(
                "first",
                label="<<",
                style=discord.ButtonStyle.blurple,
                row=self.default_button_row,
            ),
            PaginatorButton(
                "prev",
                label="<",
                style=discord.ButtonStyle.red,
                loop_label="↪",
                row=self.default_button_row,
            ),
            PaginatorButton(
                "page_indicator",
                style=discord.ButtonStyle.gray,
                disabled=True,
                row=self.default_button_row,
            ),
            PaginatorButton(
                "next",
                label=">",
                style=discord.ButtonStyle.green,
                loop_label="↩",
                row=self.default_button_row,
            ),
            PaginatorButton(
                "last",
                label=">>",
                style=discord.ButtonStyle.blurple,
                row=self.default_button_row,
            ),
        ]
        for button in default_buttons:
            self.add_button(button)

    def add_button(self, button: PaginatorButton):
        """Adds a :class:`PaginatorButton` to the paginator."""
        self.buttons[button.button_type] = {
            "object": discord.ui.Button(
                style=button.style,
                label=button.label
                if button.label or button.emoji
                else button.button_type.capitalize()
                if button.button_type != "page_indicator"
                else f"{self.current_page + 1}/{self.page_count + 1}",
                disabled=button.disabled,
                custom_id=button.custom_id,
                emoji=button.emoji,
                row=button.row,
            ),
            "label": button.label,
            "loop_label": button.loop_label,
            "hidden": button.disabled if button.button_type != "page_indicator" else not self.show_indicator,
        }
        self.buttons[button.button_type]["object"].callback = button.callback
        button.paginator = self

    def remove_button(self, button_type: str):
        """Removes a :class:`PaginatorButton` from the paginator."""
        if button_type not in self.buttons.keys():
            raise ValueError(f"no button_type {button_type} was found in this paginator.")
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
                        button["object"].label = button["label"]
                    else:
                        button["object"].label = button["loop_label"]
                elif self.current_page < self.page_count:
                    button["hidden"] = False
                    button["object"].label = button["label"]
            elif key == "prev":
                if self.current_page <= 0:
                    if not self.loop_pages:
                        button["hidden"] = True
                        button["object"].label = button["label"]
                    else:
                        button["object"].label = button["loop_label"]
                elif self.current_page >= 0:
                    button["hidden"] = False
                    button["object"].label = button["label"]
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

        if self.show_menu:
            self.add_menu()

        # We're done adding standard buttons and menus, so we can now add any specified custom view items below them
        # The bot developer should handle row assignments for their view before passing it to Paginator
        if self.custom_view:
            for item in self.custom_view.children:
                self.add_item(item)
        return self.buttons

    @staticmethod
    def get_page_content(page: Union[str, discord.Embed, List[discord.Embed]]):
        """Returns the correct content type for a page based on its content."""
        if isinstance(page, discord.Embed):
            return [page]
        elif isinstance(page, List):
            if all(isinstance(x, discord.Embed) for x in page):
                return page
            else:
                raise TypeError("All list items must be embeds.")
        elif isinstance(page, str):
            return page

    async def send(
        self,
        ctx: Context,
        target: Optional[discord.abc.Messageable] = None,
        target_message: Optional[str] = None,
    ) -> discord.Message:
        """Sends a message with the paginated items.

        Parameters
        ------------
        ctx: Union[:class:`~discord.ext.commands.Context`]
            A command's invocation context.
        target: Optional[:class:`~discord.abc.Messageable`]
            A target where the paginated message should be sent, if different from the original :class:`Context`
        target_message: Optional[:class:`str`]
            An optional message shown when the paginator message is sent elsewhere.

        Returns
        --------
        :class:`~discord.Message`
            The message that was sent with the paginator.
        """
        if not isinstance(ctx, Context):
            raise TypeError(f"expected Context not {ctx.__class__!r}")

        if target is not None and not isinstance(target, discord.abc.Messageable):
            raise TypeError(f"expected abc.Messageable not {target.__class__!r}")

        self.update_buttons()
        page = self.pages[self.current_page]
        page = self.get_page_content(page)

        self.user = ctx.author

        if target:
            if target_message:
                await ctx.send(target_message)
            ctx = target

        self.message = await ctx.send(
            content=page if isinstance(page, str) else None,
            embeds=[] if isinstance(page, str) else page,
            view=self,
        )

        return self.message

    async def respond(
        self,
        interaction: discord.Interaction,
        ephemeral: bool = False,
        target: Optional[discord.abc.Messageable] = None,
        target_message: str = "Paginator sent!",
    ) -> Union[discord.Message, discord.WebhookMessage]:
        """Sends an interaction response or followup with the paginated items.

        Parameters
        ------------
        interaction: :class:`discord.Interaction`
            The interaction which invoked the paginator.
        ephemeral: :class:`bool`
            Whether the paginator message and its components are ephemeral.
            If ``target`` is specified, the ephemeral message content will be ``target_message`` instead.
        target: Optional[:class:`~discord.abc.Messageable`]
            A target where the paginated message should be sent, if different from the original :class:`discord.Interaction`
        target_message: :class:`str`
            The content of the interaction response shown when the paginator message is sent elsewhere.

        Returns
        --------
        Union[:class:`~discord.Message`, :class:`~discord.WebhookMessage`]
            The :class:`~discord.Message` or :class:`~discord.WebhookMessage` that was sent with the paginator.
        """

        if not isinstance(interaction, discord.Interaction):
            raise TypeError(f"expected Interaction not {interaction.__class__!r}")

        if target is not None and not isinstance(target, discord.abc.Messageable):
            raise TypeError(f"expected abc.Messageable not {target.__class__!r}")

        self.update_buttons()

        page = self.pages[self.current_page]
        page = self.get_page_content(page)

        self.user = interaction.user
        if target:
            await interaction.response.send_message(target_message, ephemeral=ephemeral)
            self.message = await target.send(
                content=page if isinstance(page, str) else None,
                embeds=[] if isinstance(page, str) else page,
                view=self,
            )
        else:
            if interaction.response.is_done():
                msg = await interaction.followup.send(
                    content=page if isinstance(page, str) else None,
                    embeds=[] if isinstance(page, str) else page,
                    view=self,
                    ephemeral=ephemeral,
                )

            else:
                msg = await interaction.response.send_message(
                    content=page if isinstance(page, str) else None,
                    embeds=[] if isinstance(page, str) else page,
                    view=self,
                    ephemeral=ephemeral,
                )
            if isinstance(msg, (discord.WebhookMessage, discord.Message)):
                self.message = msg
            elif isinstance(msg, discord.Interaction):
                self.message = await msg.original_message()

        return self.message


class PaginatorMenu(discord.ui.Select):
    """Creates a select menu used to switch between page groups, which can each have their own set of buttons.

    Parameters
    ----------
    placeholder: :class:`str`
        The placeholder text that is shown if nothing is selected.

    Attributes
    ----------
    paginator: :class:`Paginator`
        The paginator class where this menu is being used.
        Assigned to the menu when ``Paginator.add_menu`` is called.
    """

    def __init__(
        self,
        page_groups: List[PageGroup],
        placeholder: str = "Select Page Group",
    ):
        self.page_groups = page_groups
        self.paginator: Optional[Paginator] = None
        opts = [
            discord.SelectOption(
                label=page_group.label,
                value=page_group.label,
                description=page_group.description,
                emoji=page_group.emoji,
            )
            for page_group in self.page_groups
        ]
        super().__init__(placeholder=placeholder, max_values=1, min_values=1, options=opts)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        for page_group in self.page_groups:
            if selection == page_group.label:
                return await self.paginator.update(
                    pages=page_group.pages,
                    show_disabled=page_group.show_disabled,
                    show_indicator=page_group.show_indicator,
                    author_check=page_group.author_check,
                    disable_on_timeout=page_group.disable_on_timeout,
                    use_default_buttons=page_group.use_default_buttons,
                    loop_pages=page_group.loop_pages,
                    custom_view=page_group.custom_view,
                    custom_buttons=page_group.custom_buttons,
                )
