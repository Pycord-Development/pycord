from typing import List, Union

import discord
from discord import abc
from discord.commands import ApplicationContext
from discord.ext.commands import Context


class PaginateButton(discord.ui.Button):
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
        self.paginator.update_buttons()
        page = self.paginator.pages[self.paginator.current_page]
        await interaction.response.edit_message(
            content=page if isinstance(page, str) else None, embed=page if isinstance(page, discord.Embed) else None, view=self.paginator
        )


class Paginate(discord.ui.View):
    """Creates a paginator for a message that is navigated with buttons.

    Parameters
    ------------
    pages: Union[List[:class:`str`], List[:class:`discord.Embed`]]
        Your list of strings or embeds to paginate
    show_disabled: :class:`bool`
        Choose whether or not to show disabled buttons
    show_indicator: :class:`bool`
        Choose whether to show the page indicator
    author_check: :class:`bool`
        Choose whether or not only the original user of the command can change pages
    custom_view: :class:`discord.ui.View`
        A custom view whose items are appended below the pagination buttons
    """

    def __init__(
        self, pages: Union[List[str], List[discord.Embed]], show_disabled=True, show_indicator=True, author_check=True, custom_view: discord.ui.View = None
    ):
        super().__init__()
        self.pages = pages
        self.current_page = 0
        self.page_count = len(self.pages) - 1
        self.show_disabled = show_disabled
        self.show_indicator = show_indicator
        self.buttons = {
            "first": {
                "object": PaginateButton(
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
                "object": PaginateButton(
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
                    label=f"{self.current_page}/{self.page_count}",
                    style=discord.ButtonStyle.gray,
                    disabled=True,
                    row=0,
                ),
                "hidden": False,
            },
            "next": {
                "object": PaginateButton(
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
                "object": PaginateButton(
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
        self.custom_view = custom_view
        self.update_buttons()

        self.usercheck = author_check
        self.user = None

    async def interaction_check(self, interaction):
        if self.usercheck:
            return self.user == interaction.user
        return True

    def customize_button(
        self, button_name: str = None, button_label: str = None, button_emoji=None, button_style: discord.ButtonStyle = discord.ButtonStyle.gray
    ) -> Union[PaginateButton, bool]:
        """Allows you to easily customize the various pagination buttons.
        Parameters
        ----------
        button_name: :class:`str`
            Name of the button to customize
        button_label: :class:`str`
            Label to display on the button
        button_emoji:
            Emoji to display on the button
        button_style: :class:`~discord.ButtonStyle`
            ButtonStyle to use for the button

        Returns
        -------
        :class:`~PaginateButton`
            The button that was customized
        """

        if button_name not in self.buttons.keys():
            return False
        button: PaginateButton = self.buttons[button_name]["object"]
        button.label = button_label
        button.emoji = button_emoji
        button.style = button_style
        return button

    def update_buttons(self):
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
            self.buttons["page_indicator"]["object"].label = f"{self.current_page}/{self.page_count}"
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

        if self.custom_view:
            for item in self.custom_view.children:
                self.add_item(item)

    async def send(self, messageable: abc.Messageable, ephemeral: bool = False):
        """Sends a message with the paginated items.
        Parameters
        ------------
        messageable: :class:`discord.abc.Messageable`
            The messageable channel to send to.
        ephemeral: :class:`bool`
            Choose whether or not the message is ephemeral. Only works with slash commands.
        Returns
        --------
        :class:`~discord.Message`
            The message that was sent.
        """

        if not isinstance(messageable, abc.Messageable):
            raise TypeError("messageable should be a subclass of abc.Messageable")

        page = self.pages[0]

        if isinstance(messageable, (ApplicationContext, Context)):
            self.user = messageable.author

        return (
            await messageable.respond(
                content=page if isinstance(page, str) else None,
                embed=page if isinstance(page, discord.Embed) else None,
                view=self,
                ephemeral=ephemeral,
            )
            if isinstance(messageable, ApplicationContext)
            else await messageable.send(
                content=page if isinstance(page, str) else None,
                embed=page if isinstance(page, discord.Embed) else None,
                view=self,
            )
        )
