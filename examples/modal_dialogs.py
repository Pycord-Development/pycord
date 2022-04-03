import discord
from discord.ext import commands
from discord.ui import InputText, Modal


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=">")


bot = Bot()


class MyModal(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label="Short Input", placeholder="Placeholder Test"))

        self.add_item(
            InputText(
                label="Longer Input",
                value="Longer Value\nSuper Long Value",
                style=discord.InputTextStyle.long,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Your Modal Results", color=discord.Color.random())
        embed.add_field(name="First Input", value=self.children[0].value, inline=False)
        embed.add_field(name="Second Input", value=self.children[1].value, inline=False)
        await interaction.response.send_message(embeds=[embed])


@bot.slash_command(name="modaltest", guild_ids=[...])
async def modal_slash(ctx):
    """Shows an example of a modal dialog being invoked from a slash command."""
    modal = MyModal(title="Slash Command Modal")
    await ctx.send_modal(modal)


@bot.message_command(name="messagemodal", guild_ids=[...])
async def modal_message(ctx, message):
    """Shows an example of a modal dialog being invoked from a message command."""
    modal = MyModal(title="Message Command Modal")
    modal.title = f"Modal for Message ID: {message.id}"
    await ctx.send_modal(modal)


@bot.user_command(name="usermodal", guild_ids=[...])
async def modal_user(ctx, member):
    """Shows an example of a modal dialog being invoked from a user command."""
    modal = MyModal(title="User Command Modal")
    modal.title = f"Modal for User: {member.display_name}"
    await ctx.send_modal(modal)


@bot.command()
async def modaltest(ctx):
    """Shows an example of modals being invoked from an interaction component (e.g. a button or select menu)"""

    class MyView(discord.ui.View):
        @discord.ui.button(label="Modal Test", style=discord.ButtonStyle.primary)
        async def button_callback(self, button, interaction):
            modal = MyModal(title="Modal Triggered from Button")
            await interaction.response.send_modal(modal)

        @discord.ui.select(
            placeholder="Pick Your Modal",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="First Modal", description="Shows the first modal"),
                discord.SelectOption(label="Second Modal", description="Shows the second modal"),
            ],
        )
        async def select_callback(self, select, interaction):
            modal = MyModal(title="Temporary Title")
            modal.title = select.values[0]
            await interaction.response.send_modal(modal)

    view = MyView()
    await ctx.send("Click Button, Receive Modal", view=view)


bot.run("your token")
