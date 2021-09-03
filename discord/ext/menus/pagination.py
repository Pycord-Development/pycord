import discord, asyncio
from typing import List, Union

from discord import abc
from discord.interactions import Interaction
from discord.utils import MISSING
from discord.ui.button import button


class Paginate(discord.ui.View):
    """Creates a paginator for embeds that is navigated with buttons.
    
    Parameters
    ------------
    messageable: :class:`discord.abc.Messageable`
        The messageable channel to send to.

    pages: Union[List[:class:`str`], List[:class:`discord.Embed`]]
        Your list of strings or embeds to paginate

    show_disabled: :class:`bool`
        Choose whether or not to show disabled buttons

    """

    def __init__(self, messageable: abc.Messageable, pages: Union[List[str], List[discord.Embed]], show_disabled = True):
        super().__init__()
        self.messageable = messageable
        self.pages = pages
        self.current_page = 1
        self.page_count = len(self.pages)
        self.show_disabled = show_disabled
        self.forbutton = self.children[1]
        self.prevbutton= self.children[0]
        if not self.show_disabled:
            self.remove_item(self.children[0])
            if self.page_count == 1:
                self.remove_item(self.children[1])

    @discord.ui.button(label = "<", style = discord.ButtonStyle.green, disabled=True)
    async def previous(self, button: discord.ui.Button, interaction = discord.Interaction):
        self.current_page -= 1

        if self.current_page == 1:
            button.disabled = True

        if not self.show_disabled:
            if len(self.children) == 1:
                self.add_item(self.forbutton)
                self.forbutton.disabled = False
            if button.disabled:
                self.remove_item(button)
        else:
            self.children[1].disabled = False

        page = self.pages[self.current_page-1]
        await interaction.response.edit_message(content = page if isinstance(page, str) else None, embed = page if isinstance(page, discord.Embed) else MISSING , view = self)

    @discord.ui.button(label = '>', style=discord.ButtonStyle.green)
    async def forward(self, button: discord.ui.Button, interaction = discord.Interaction): 
        self.current_page += 1

        if self.current_page == self.page_count:
            button.disabled = True
    
        if not self.show_disabled: 
            if len(self.children) == 1:
                self.add_item(self.prevbutton)
                self.prevbutton.disabled = False
                self.children[0], self.children[1] = self.children[1], self.children[0]
            if button.disabled:
                self.remove_item(button)
        else:
            self.children[0].disabled = False

        page = self.pages[self.current_page-1]
        await interaction.response.edit_message(content = page if isinstance(page, str) else None, embed = page if isinstance(page, discord.Embed) else MISSING, view = self)

    async def send(self):
        """Sends a message with the paginated items.
        
        Returns
        --------
        :class:`~discord.Message`
            The message that was sent.
        """

        if not isinstance(self.messageable, abc.Messageable):
            raise TypeError("messageable is not a messageable object")
        page = self.pages[0]
        message = await self.messageable.send(content = page if isinstance(page, str) else None, embed = page if isinstance(page, discord.Embed) else MISSING if isinstance(self.messageable, discord.app.context.InteractionContext) else None, view = self)
        return message

    def forward_button(self, label: str, color: str = "green"):
        """Customize your forward button
        
        Parameters
        ------------
        label: :class:`str`
            The text you want on your button
            
        color: :class:`str`
            The color of the button.
            
        Raises
        --------
        AttributeError
            The color provided isn't supported
            """

        self.forbutton.label = label
        color = getattr(discord.ButtonStyle, color.lower())
        self.forbutton.style = color

    def back_button(self, label: str, color: str = "green"):
        """Customize your back button
        
        Parameters
        ------------
        label: :class:`str`
            The text you want on your button
            
        color: :class:`str`
            The color of the button.
            
        Raises
        --------
        AttributeError
            The color provided isn't supported
            """

        self.prevbutton.label = label
        color = getattr(discord.ButtonStyle, color.lower())
        self.prevbutton.style = color
