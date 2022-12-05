# This example requires the `message_content` privileged intent for prefixed commands.

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"), debug_guilds=[...], intents=intents
)


class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            discord.ui.InputText(
                label="Short Input",
                placeholder="Placeholder Test",
            ),
            discord.ui.InputText(
                label="Longer Input",
                value="Longer Value\nSuper Long Value",
                style=discord.InputTextStyle.long,
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Your Modal Results",
            fields=[
                discord.EmbedField(
                    name="First Input", value=self.children[0].value, inline=False
                ),
                discord.EmbedField(
                    name="Second Input", value=self.children[1].value, inline=False
                ),
            ],
            color=discord.Color.random(),
        )
        await interaction.response.send_message(embeds=[embed])


@bot.slash_command(name="modaltest")
async def modal_slash(ctx: discord.ApplicationContext):
    """Shows an example of a modal dialog being invoked from a slash command."""
    modal = MyModal(title="Slash Command Modal")
    await ctx.send_modal(modal)


@bot.message_command(name="messagemodal")
async def modal_message(ctx: discord.ApplicationContext, message: discord.Message):
    """Shows an example of a modal dialog being invoked from a message command."""
    modal = MyModal(title="Message Command Modal")
    modal.title = f"Modal for Message ID: {message.id}"
    await ctx.send_modal(modal)


@bot.user_command(name="usermodal")
async def modal_user(ctx: discord.ApplicationContext, member: discord.Member):
    """Shows an example of a modal dialog being invoked from a user command."""
    modal = MyModal(title="User Command Modal")
    modal.title = f"Modal for User: {member.display_name}"
    await ctx.send_modal(modal)


@bot.command()
async def modaltest(ctx: commands.Context):
    """Shows an example of modals being invoked from an interaction component (e.g. a button or select menu)"""

    class MyView(discord.ui.View):
        @discord.ui.button(label="Modal Test", style=discord.ButtonStyle.primary)
        async def button_callback(
            self, button: discord.ui.Button, interaction: discord.Interaction
        ):
            modal = MyModal(title="Modal Triggered from Button")
            await interaction.response.send_modal(modal)

        @discord.ui.select(
            placeholder="Pick Your Modal",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label="First Modal", description="Shows the first modal"
                ),
                discord.SelectOption(
                    label="Second Modal", description="Shows the second modal"
                ),
            ],
        )
        async def select_callback(
            self, select: discord.ui.Select, interaction: discord.Interaction
        ):
            modal = MyModal(title="Temporary Title")
            modal.title = select.values[0]
            await interaction.response.send_modal(modal)

    view = MyView()
    await ctx.send("Click Button, Receive Modal", view=view)


bot.run("TOKEN")
