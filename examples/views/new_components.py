from io import BytesIO

from discord import (
    ApplicationContext,
    Bot,
    ButtonStyle,
    Color,
    File,
    Interaction,
    SeparatorSpacingSize,
    User,
)
from discord.ui import (
    Button,
    Container,
    MediaGallery,
    Section,
    Select,
    Separator,
    TextDisplay,
    Thumbnail,
    DesignerView,
    ActionRow,
    button,
)

class MyRow(ActionRow):

    @button(label="Delete Message", style=ButtonStyle.red, id=200)
    async def delete_button(self, button: Button, interaction: Interaction):
        await interaction.response.defer(invisible=True)
        await interaction.message.delete()

class MyView(DesignerView):
    def __init__(self, user: User):
        super().__init__(timeout=30)
        text1 = TextDisplay("### This is a sample `TextDisplay` in a `Section`.")
        text2 = TextDisplay(
            "This section is contained in a `Container`.\nTo the right, you can see a `Thumbnail`."
        )
        thumbnail = Thumbnail(user.display_avatar.url)

        section = Section(text1, text2, accessory=thumbnail)
        section.add_text("-# Small text")

        container = Container(
            section,
            TextDisplay("Another `TextDisplay` separate from the `Section`."),
            color=Color.blue(),
        )
        container.add_separator(divider=True, spacing=SeparatorSpacingSize.large)
        container.add_item(Separator())
        container.add_file("attachment://sample.png")
        container.add_text("Above is two `Separator`s followed by a `File`.")

        gallery = MediaGallery()
        gallery.add_item(user.default_avatar.url)
        gallery.add_item(user.avatar.url)

        self.add_item(container)
        self.add_item(gallery)
        self.add_item(
            TextDisplay("Above is a `MediaGallery` containing two `MediaGalleryItem`s.")
        )
        row = MyRow()
        self.add_item(row)

    async def on_timeout(self):
        self.get_item(200).disabled = True
        await self.parent.edit(view=self)


bot = Bot()


@bot.command()
async def show_view(ctx: ApplicationContext):
    """Display a sample View showcasing various new components."""

    f = await ctx.author.display_avatar.read()
    file = File(BytesIO(f), filename="sample.png")
    await ctx.respond(view=MyView(ctx.author), files=[file])


bot.run("TOKEN")
