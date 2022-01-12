import discord
from discord.commands.core import slash_command
from discord.ext import commands

"""
Let users assign themselves roles by clicking on Buttons.
The view made is persistent, so it will work even when the bot restarts.

See this example for more information about persistent views
https://github.com/Pycord-Development/pycord/blob/master/examples/views/persistent.py
Make sure to load this cog when your bot starts!
"""

# this is the list of role IDs that will be added as buttons.
role_ids = [...]


class RoleButton(discord.ui.Button):
    def __init__(self, role: discord.Role):
        """
        A button for one role. `custom_id` is needed for persistent views.
        """
        super().__init__(
            label=role.name,
            style=discord.enums.ButtonStyle.primary,
            custom_id=str(role.id),
        )

    async def callback(self, interaction: discord.Interaction):
        """This function will be called any time a user clicks on this button

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object that was created when the user clicked on the button
        """

        # figure out who clicked the button
        user = interaction.user
        # get the role this button is for (stored in the custom ID)
        role = interaction.guild.get_role(int(self.custom_id))

        if role is None:
            # if this role doesn't exist, ignore
            # you can do some error handling here
            return

        # passed all checks
        # add the role and send a response to the uesr ephemerally (hidden to other users)
        if role not in user.roles:
            # give the user the role if they don't already have it
            await user.add_roles(role)
            await interaction.response.send_message(
                f"🎉 You have been given the role {role.mention}", ephemeral=True
            )
        else:
            # else, take the role from the user
            await user.remove_roles(role)
            await interaction.response.send_message(
                f"❌ The {role.mention} role has been taken from you", ephemeral=True
            )


class ButtonRoleCog(commands.Cog):
    """A cog with a slash command for posting the message with buttons
    and to initialize the view again when the bot is restarted
    """

    def __init__(self, bot):
        self.bot = bot

    # make sure to set the guild ID here to whatever server you want the buttons in
    @slash_command(guild_ids=[...], description="Post the button role message")
    async def post(self, ctx: commands.Context):
        """A slash command to post a new view with a button for each role"""

        # timeout is None because we want this view to be persistent
        view = discord.ui.View(timeout=None)

        # loop through the list of roles and add a new button to the view for each role
        for role_id in role_ids:
            # get the role the guild by ID
            role = ctx.guild.get_role(role_id)
            view.add_item(RoleButton(role))

        await ctx.respond("Click a button to assign yourself a role", view=view)

    @commands.Cog.listener()
    async def on_ready(self):
        """This function is called every time the bot restarts.
        If a view was already created before (with the same custom IDs for buttons)
        it will be loaded and the bot will start watching for button clicks again.
        """

        # we recreate the view as we did in the /post command
        view = discord.ui.View(timeout=None)
        # make sure to set the guild ID here to whatever server you want the buttons in
        guild = self.bot.get_guild(...)
        for role_id in role_ids:
            role = guild.get_role(role_id)
            view.add_item(RoleButton(role))

        # add the view to the bot so it will watch for button interactions
        self.bot.add_view(view)


def setup(bot):
    # load the cog
    bot.add_cog(ButtonRoleCog(bot))
