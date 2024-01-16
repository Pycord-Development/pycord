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
from __future__ import annotations
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from .buttons import PaginatorButton

__all__ = (
    "Page",
    "PageGroup",
)


class Page:
    """Represents a page shown in the paginator.

    Allows for directly referencing and modifying each page as a class instance.

    Parameters
    ----------
    content: :class:`str`
        The content of the page. Corresponds to the :class:`discord.Message.content` attribute.
    embeds: Optional[List[Union[List[:class:`discord.Embed`], :class:`discord.Embed`]]]
        The embeds of the page. Corresponds to the :class:`discord.Message.embeds` attribute.
    files: Optional[List[:class:`discord.File`]]
        A list of local files to be shown with the page.
    custom_view: Optional[:class:`discord.ui.View`]
        The custom view shown when the page is visible. Overrides the `custom_view` attribute of the main paginator.
    """

    def __init__(
        self,
        content: str | None = None,
        embeds: list[list[discord.Embed]] | list[discord.Embed] | None = None,
        custom_view: discord.ui.View | None = None,
        files: list[discord.File] | None = None,
    ):
        if content is None and embeds is None:
            raise discord.InvalidArgument(
                "A page cannot have both content and embeds equal to None."
            )
        self.content = content
        self.embeds = embeds or []
        self.custom_view = custom_view
        self.files = files or []

    async def callback(self, interaction: discord.Interaction | None = None):
        """|coro|

        The coroutine associated to a specific page. If `Paginator.page_action()` is used, this coroutine is called.

        Parameters
        ----------
        interaction: Optional[:class:`discord.Interaction`]
            The interaction associated with the callback, if any.
        """

    def update_files(self) -> list[discord.File] | None:
        """Updates :class:`discord.File` objects so that they can be sent multiple
        times. This is called internally each time the page is sent.
        """
        for file in self.files:
            if file.fp.closed and (fn := getattr(file.fp, "name", None)):
                file.fp = open(fn, "rb")
            file.reset()
            file.fp.close = lambda: None
        return self.files


class PageGroup:
    """Creates a group of pages which the user can switch between.

    Each group of pages can have its own options, custom buttons, custom views, etc.

    .. note::

        If multiple :class:`PageGroup` objects have different options,
        they should all be set explicitly when creating each instance.

    Parameters
    ----------
    pages: Union[List[:class:`str`], List[:class:`Page`], List[:class:`discord.Embed`], List[:class:`discord.Embed`]]
        The list of :class:`Page` objects, strings, embeds, or list of embeds to include in the page group.
    label: :class:`str`
        The label shown on the corresponding PaginatorMenu dropdown option.
        Also used as the SelectOption value.
    description: Optional[:class:`str`]
        The description shown on the corresponding PaginatorMenu dropdown option.
    emoji: Optional[:class:`str`, :class:`discord.Emoji`, :class:`discord.PartialEmoji`]
        The emoji shown on the corresponding PaginatorMenu dropdown option.
    default: Optional[:class:`bool`]
        Whether the page group should be the default page group initially shown when the paginator response is sent.
        Only one ``PageGroup`` can be the default page group.
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
    trigger_on_display: :class:`bool`
        Whether to automatically trigger the callback associated with a `Page` whenever it is displayed.
        Has no effect if no callback exists for a `Page`.
    """

    def __init__(
        self,
        pages: (
            list[str] | list[Page] | list[list[discord.Embed]] | list[discord.Embed]
        ),
        label: str,
        description: str | None = None,
        emoji: str | discord.Emoji | discord.PartialEmoji | None = None,
        default: bool | None = None,
        show_disabled: bool | None = None,
        show_indicator: bool | None = None,
        author_check: bool | None = None,
        disable_on_timeout: bool | None = None,
        use_default_buttons: bool | None = None,
        default_button_row: int = 0,
        loop_pages: bool | None = None,
        custom_view: discord.ui.View | None = None,
        timeout: float | None = None,
        custom_buttons: list[PaginatorButton] | None = None,
        trigger_on_display: bool | None = None,
    ):
        self.label = label
        self.description: str | None = description
        self.emoji: str | discord.Emoji | discord.PartialEmoji | None = emoji
        self.pages: list[str] | list[Page] | list[list[discord.Embed]] | list[
            discord.Embed
        ] = pages
        self.default: bool | None = default
        self.show_disabled = show_disabled
        self.show_indicator = show_indicator
        self.author_check = author_check
        self.disable_on_timeout = disable_on_timeout
        self.use_default_buttons = use_default_buttons
        self.default_button_row = default_button_row
        self.loop_pages = loop_pages
        self.custom_view: discord.ui.View | None = custom_view
        self.timeout: float | None = timeout
        self.custom_buttons: list | None = custom_buttons
        self.trigger_on_display = trigger_on_display
