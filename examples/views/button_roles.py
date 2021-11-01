import discord
from discord.commands.commands import slash_command

from discord.ext import commands
"""
Let users assign themselves roles by clicking on Buttons
Make sure to add the cog to the initial_extensions list
in main.py
"""

# I chose to have emojis in my buttons 
# you could also do this as just a list of role IDs
emoji_to_role_id = {
    "<:gircoin:846511056137748571>": "846383888003760217",
    "<a:GirDance:846510964463239199>": "846383888036134932"
}

class RoleButton(discord.ui.Button):
    def __init__(self, role: discord.Role, emoji):
        super().__init__(label=role.name, style=discord.enum.ButtonStyle.primary, emoji=emoji, custom_id=str(role.id))
        self.emoji = emoji
    
    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        role = interaction.guild.get_role(int(self.custom_id))
        if role is None:
            return
        
        if role not in user.roles:
            await user.add_roles(role)
            await interaction.response.send_message(f"{self.emoji} You have been given the role {role.mention}", ephemeral=True)
        else:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{self.emoji} You have been removed the role {role.mention}", ephemeral=True)

class ButtonRoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[123], description="Post the button role message")
    async def post(self, ctx: commands.Context):
        # timeout is None because we want this view to be persistent
        view = discord.ui.View(timeout=None)
        
        # loop through the dict of roles and add them to the view
        for emoji, role_id in emoji_to_role_id.items():
            role = ctx.guild.get_role(int(role_id))
            view.add_item(RoleButton(role, emoji))

        await ctx.respond("Click a button to assign yourself a role", view=view)
        
    @commands.Cog.listener()
    async def on_ready(self):
        # this function is run when the bot is started.
        # we recreate the view as we did in the /post command
        view = discord.ui.View(timeout=None)
        guild = self.bot.get_guild(123)
        for emoji, role_id in emoji_to_role_id.items():
            role = guild.get_role(int(role_id))
            view.add_item(RoleButton(role, emoji))

        # add the view to the bot so it will watch for button interactions
        self.bot.add_view(view)

def setup(bot):
    bot.add_cog(ButtonRoleCog(bot))
