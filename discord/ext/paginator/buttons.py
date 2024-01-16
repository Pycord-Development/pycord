from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from .pages import PageGroup
    from .paginator import Paginator

__all__ = (
    "PaginatorButtonType",
    "PaginatorButton",
    "PaginatorMenu",
)


class PaginatorButtonType(Enum):
    first = 1
    prev = 2
    page_indicator = 3
    next = 4
    last = 5


class PaginatorButton(discord.ui.Button):
    """Creates a button used to navigate the paginator.

    Parameters
    ----------
    button_type: :class:`PaginatorButtonType`
        The type of button being created.
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
    base_label: :class:`str`
        The label shown on the button when ``loop_pages`` is set to ``False`` in the Paginator class.
        This is initialized to the ``label`` parameter, but can be changed later.
    hidden: :class:`bool`
        Whether the button is hidden or not.
        This is initialized to the ``disabled`` parameter, but can be changed later.
    """

    def __init__(
        self,
        button_type: PaginatorButtonType,
        label: str | None = None,
        emoji: str | discord.Emoji | discord.PartialEmoji | None = None,
        style: discord.ButtonStyle = discord.ButtonStyle.green,
        disabled: bool = False,
        custom_id: str | None = None,
        row: int = 0,
        loop_label: str | None = None,
    ):
        super().__init__(
            label=label if label or emoji else button_type.name.capitalize(),
            emoji=emoji,
            style=style,
            disabled=disabled,
            custom_id=custom_id,
            row=row,
        )
        self.button_type = button_type
        self.base_label = str(self.label) if self.label else None
        self.loop_label = self.label if not loop_label else loop_label
        self.hidden = disabled
        self.paginator: Paginator  # | None = None

    async def callback(self, interaction: discord.Interaction):
        """|coro|

        The coroutine that is called when the navigation button is clicked.

        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            The interaction created by clicking the navigation button.
        """
        if self.button_type == PaginatorButtonType.first:
            self.paginator.current_page = 0
        elif self.button_type == PaginatorButtonType.prev:
            if self.paginator.loop_pages and self.paginator.current_page == 0:
                self.paginator.current_page = self.paginator.page_count
            else:
                self.paginator.current_page -= 1
        elif self.button_type == PaginatorButtonType.next:
            if (
                self.paginator.loop_pages
                and self.paginator.current_page == self.paginator.page_count
            ):
                self.paginator.current_page = 0
            else:
                self.paginator.current_page += 1
        elif self.button_type == PaginatorButtonType.last:
            self.paginator.current_page = self.paginator.page_count
        await self.paginator.goto_page(
            page_number=self.paginator.current_page, interaction=interaction
        )


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
        page_groups: list[PageGroup],
        placeholder: str | None = None,
        custom_id: str | None = None,
    ):
        self.page_groups = page_groups
        self.paginator: Paginator  # | None = None
        opts = [
            discord.SelectOption(
                label=page_group.label,
                value=page_group.label,
                description=page_group.description,
                emoji=page_group.emoji,
            )
            for page_group in self.page_groups
        ]
        super().__init__(
            placeholder=placeholder,
            max_values=1,
            min_values=1,
            options=opts,
            custom_id=custom_id,
        )

    async def callback(self, interaction: discord.Interaction):
        """|coro|

        The coroutine that is called when a menu option is selected.

        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            The interaction created by selecting the menu option.
        """
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
                    default_button_row=page_group.default_button_row,
                    loop_pages=page_group.loop_pages,
                    custom_view=page_group.custom_view,
                    timeout=page_group.timeout,
                    custom_buttons=page_group.custom_buttons,
                    trigger_on_display=page_group.trigger_on_display,
                    interaction=interaction,
                )
