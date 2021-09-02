import discord, asyncio
from typing import List, Union

from discord import abc
from discord.ui.button import button

class Paginate(discord.ui.View):
    """Creates a paginator for embeds that is navigated with buttons.
    
    Parameters
    ------------
    messageable: :class:`discord.abc.Messageable`
        The messageable channel to send to.

    embeds: List[:class:`discord.Embed`]
        Your list of embeds to paginate

    hide_disabled: :class:`bool`
        Choose whether or not to hide disabled buttons
    """

    def __init__(self, messageable: abc.Messageable, embeds: List[discord.Embed], hide_disabled = False):
        super().__init__()
        self.messageable = messageable
        self.embeds = embeds
        self.current_page = 1
        self.page_count = len(self.embeds)
        self.hide_disabled = hide_disabled
        self.forbutton = None
        self.prevbutton= None

    @discord.ui.button(label = "<", style = discord.ButtonStyle.green, disabled=True)
    async def previous(self, button: discord.ui.Button, interaction = discord.Interaction):
        self.current_page -= 1

        if self.current_page == 1:
            button.disabled = True

        if self.hide_disabled:
            if len(self.children) == 1:
                self.add_item(self.forbutton)
                self.forbutton.disabled = False
            if button.disabled:
                self.remove_item(button)
        else:
            self.children[1].disabled = False

        await interaction.response.edit_message(embed = self.embeds[self.current_page-1], view = self)

    @discord.ui.button(label = '>', style=discord.ButtonStyle.green)
    async def forward(self, button: discord.ui.Button, interaction = discord.Interaction):
        
        self.current_page += 1
        
        if self.current_page == self.page_count:
            button.disabled = True

        if self.hide_disabled: 
            if len(self.children) == 1:
                self.add_item(self.prevbutton)
                self.prevbutton.disabled = False
                self.children[0], self.children[1] = self.children[1], self.children[0]
            if button.disabled:
                self.remove_item(button)
        else:
            self.children[0].disabled = False

        await interaction.response.edit_message(embed = self.embeds[self.current_page-1], view = self)

    async def send(self):
        """Sends a message with the paginated embeds."""
        self.prevbutton = self.children[0]
        self.forbutton = self.children[1]
        if self.page_count == 1:
            self.children[1].disabled = True
            if self.hide_disabled:
                self.remove_item(self.children[1])
        if self.hide_disabled:
            self.remove_item(self.children[0])
        if not isinstance(self.messageable, abc.Messageable):
            raise TypeError("messageable is not a messageable object")
        await self.messageable.send(embed = self.embeds[0], view = self)
