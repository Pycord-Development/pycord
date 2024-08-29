from __future__ import annotations

import base64
import io
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

import discord


class WaveformVisualizer:
    """
    A class to visualize audio waveforms.

    Attributes
    ----------
    waveform_byte_data : numpy.ndarray
        The decoded waveform byte data.

    Methods
    -------
    decode_waveform(base64_waveform: str) -> np.ndarray[Any, np.dtype[np.uint8]]:
        Decodes the base64 encoded waveform string into a numpy array.

    create_waveform_image(width: int = 500, height: int = 100,
                          background_color: Union[float, tuple[float, ...], str, None] = (0, 0, 0),
                          bar_colors: Union[None, list[tuple[int, int, int]]] = None) -> Image.Image:
        Creates a visual representation of the waveform as an image.
    """

    def __init__(self, base64_waveform: str) -> None:
        """
        Initializes the WaveformVisualizer with the provided base64 waveform string.

        Parameters
        ----------
        base64_waveform : str
            A base64 encoded string representing the waveform.
        """
        self.waveform_byte_data: np.ndarray[Any, np.dtype[np.uint8]] = (
            self.decode_waveform(base64_waveform)
        )

    @staticmethod
    def decode_waveform(base64_waveform: str) -> np.ndarray[Any, np.dtype[np.uint8]]:
        """
        Decodes the base64 encoded waveform string into a numpy array.

        Parameters
        ----------
        base64_waveform : str
            The base64 encoded string of the waveform.

        Returns
        -------
        np.ndarray
            A numpy array containing the decoded waveform byte data.
        """
        return np.frombuffer(base64.b64decode(base64_waveform), dtype=np.uint8)

    def create_waveform_image(
        self,
        width: int = 500,
        height: int = 100,
        background_color: float | tuple[float, ...] | str | None = (0, 0, 0),
        bar_colors: None | list[tuple[int, int, int]] = None,
    ) -> Image.Image:
        """
        Creates a visual representation of the waveform as an image.

        Parameters
        ----------
        width : int, optional
            The width of the resulting image, by default 500.
        height : int, optional
            The height of the resulting image, by default 100.
        background_color : float | tuple[float, ...] | str | None, optional
            The background color of the image, by default (0, 0, 0).
        bar_colors : list[tuple[int, int, int]] | None, optional
            A list of colors for the waveform bars, by default None.

        Returns
        -------
        Image.Image
            A PIL Image object representing the waveform.
        """
        # If no bar colors are provided, default to a predefined gradient of blue shades.
        if bar_colors is None:
            bar_colors = [(173, 216, 230), (135, 206, 235), (0, 191, 255)]
            # These RGB tuples represent light shades of blue, commonly associated with a calm, cool color palette.

        # Create a new blank image with the specified background color.
        # The image will be RGB (Red, Green, Blue) format, with the given width and height.
        # The background color fills the entire image initially.
        image = Image.new("RGB", (width, height), background_color)

        # Initialize the ImageDraw object to draw on the image.
        # The 'draw' object will be used to draw shapes (like rectangles) on the 'image'.
        draw = ImageDraw.Draw(image)

        # Calculate the width of each bar in the waveform visualization.
        # The total width of the image is divided by twice the number of waveform data points.
        # This division ensures that the bars are narrow enough to fit into the image, with some spacing between them.
        bar_width = width / len(self.waveform_byte_data) / 2

        # Calculate the scaling factor for the X-axis (horizontal scale).
        # This factor determines the horizontal spacing between the bars.
        # It ensures that the bars are evenly spaced across the entire width of the image.
        x_scale = width / len(self.waveform_byte_data)

        # Calculate the scaling factor for the Y-axis (vertical scale).
        # The height of the image is divided by twice the maximum possible waveform value (255),
        # as the waveform values range from 0 to 255.
        # This scaling ensures that the waveform is vertically centered in the image and that the bars are proportional to the waveform's amplitude.
        y_scale = height / 2 / 255

        for i, value in enumerate(self.waveform_byte_data):
            # Check if the current value is a tuple. In some cases, the waveform data might be stored as a tuple (e.g., (value,)).
            # If it is a tuple, extract the first item to get the actual waveform value.
            if isinstance(value, tuple):
                value = value[
                    0
                ]  # Extract the first item from the tuple, which is the actual waveform value.

            # Calculate the X position of the current bar.
            # The position is determined by the index of the current value (i) multiplied by the scaling factor (x_scale).
            x1 = i * x_scale

            # Calculate the height of the bar representing the waveform at this point.
            # The height is determined by multiplying the waveform value (converted to a float) by the Y scaling factor (y_scale).
            # The `max` function ensures that the bar has a minimum height of 2.0, even if the waveform value is very small.
            bar_height = max(2.0, float(value) * y_scale)

            # Calculate the Y position of the top of the bar.
            # This is done by subtracting the bar's height from half the total height, so the bar extends upwards from the middle of the image.
            y1 = height / 2 - bar_height

            # Calculate the Y position of the bottom of the bar.
            # This is simply half the height of the image plus the bar's height, so the bar also extends downwards from the middle of the image.
            y2 = height / 2 + bar_height

            # Determine the color of the bar.
            # The color is chosen from the `bar_colors` list, cycling through the colors using the modulo operator (`%`).
            # This ensures that the colors repeat in a loop if there are more bars than colors.
            color_index = i % len(bar_colors)
            color = bar_colors[color_index]

            # Draw the rectangle (bar) for this part of the waveform on the image.
            # The rectangle is drawn from (x1, y1) to (x1 + bar_width, y2) using the selected color.
            draw.rectangle([x1, y1, x1 + bar_width, y2], fill=color)

        return image


# Discord bot setup with specific intents (permissions)
intents = discord.Intents.default()
intents.message_content = True  # Enables access to message content
intents.members = True  # Enables access to server members

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready() -> None:
    """
    Event handler for when the bot is ready.

    This method is called automatically by the pycord library when the bot has successfully connected to Discord
    and is ready to start receiving events and commands.
    """
    print("Ready!")


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    Event handler for when a message is received.

    This method is called automatically whenever a new message is sent in any channel the bot can access.

    Parameters
    ----------
    message : discord.Message
        The message object containing information about the message sent.
    """
    if message.author.id == bot.user.id:
        return  # Ignore messages sent by the bot itself

    if (
        message.attachments and len(message.attachments) == 1
    ):  # Check if there's exactly one attachment
        target_attachment = message.attachments[0]
        if (
            target_attachment.content_type == "audio/ogg"
            and target_attachment.filename == "voice-message.ogg"
        ):  # Check if the attachment is a voice message
            print("We got a voice message!")
            await handle_voice_message(message, target_attachment)


async def handle_voice_message(
    message: discord.Message, attachment: discord.Attachment
) -> None:
    """
    Handles the processing of voice message attachments.

    Converts the waveform of the voice message to a visual image and sends it back in an embed.

    Parameters
    ----------
    message : discord.Message
        The message object containing the voice message.
    attachment : discord.Attachment
        The attachment object representing the voice message.
    """
    # Create a visual image of the waveform using the WaveformVisualizer class
    image = WaveformVisualizer(attachment.waveform).create_waveform_image()

    # Save the image to a byte buffer in PNG format
    image_buffer = io.BytesIO()
    image.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    # Create a discord.File object from the byte buffer to send as an attachment
    file = discord.File(
        image_buffer, "waveform.png", description="A neat waveform image!"
    )

    # Create an embed to display information and the image
    embed = discord.Embed()
    embed.set_author(
        name=message.author.display_name, icon_url=message.author.display_avatar
    )
    embed.title = "Voice Message"
    embed.add_field(name="Duration", value=str(attachment.duration_secs))
    embed.set_image(url="attachment://waveform.png")
    embed.timestamp = message.created_at

    # Reply to the original message with the embed and attached waveform image
    await message.reply(None, embed=embed, file=file)


# Run the bot with the provided token
bot.run("TOKEN")
