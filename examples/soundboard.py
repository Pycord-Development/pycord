import asyncio
import logging
import os

from dotenv import load_dotenv

import discord

logging.basicConfig(level=logging.INFO)

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = discord.Bot()


class SoundboardCog(discord.Cog):
    """A cog demonstrating Discord's soundboard features."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_voice_channel_effect_send(
        self, event: discord.VoiceChannelEffectSendEvent
    ):
        """Called when someone uses a soundboard effect in a voice channel."""
        if event.sound:
            print(f"{event.user} played sound '{event.sound.name}' in {event.channel}")
        elif event.emoji:
            print(f"{event.user} sent emoji effect {event.emoji} in {event.channel}")

    @discord.slash_command()
    async def list_sounds(self, ctx: discord.ApplicationContext):
        """Lists all the available sounds in the guild."""
        await ctx.defer()

        # Fetch both default and guild-specific sounds
        default_sounds = await self.bot.fetch_default_sounds()
        guild_sounds = await ctx.guild.fetch_sounds()

        embed = discord.Embed(title="Available Sounds")

        # List default sounds
        if default_sounds:
            default_list = "\n".join(
                f"{s.emoji} {s.name} (Volume: {s.volume})" for s in default_sounds
            )
            embed.add_field(
                name="Default Sounds", value=default_list or "None", inline=False
            )

        # List guild sounds
        if guild_sounds:
            guild_list = "\n".join(
                f"{s.emoji} {s.name} (Volume: {s.volume})" for s in guild_sounds
            )
            embed.add_field(
                name="Guild Sounds", value=guild_list or "None", inline=False
            )

        await ctx.respond(embed=embed)

    @discord.slash_command()
    @discord.default_permissions(manage_guild=True)
    async def add_sound(
        self,
        ctx: discord.ApplicationContext,
        name: str,
        emoji: str,
        attachment: discord.Attachment,
    ):
        """Adds a new sound to the guild's soundboard. Currently only supports mp3 files."""
        await ctx.defer()

        if not attachment.content_type.startswith("audio/"):
            return await ctx.respond("Please upload an audio file!")

        try:
            sound_bytes = await attachment.read()
            emoji = discord.PartialEmoji.from_str(emoji)

            new_sound = await ctx.guild.create_sound(
                name=name, sound=sound_bytes, volume=1.0, emoji=emoji
            )

            await ctx.respons(f"Added new sound: {new_sound.emoji} {new_sound.name}")
        except Exception as e:
            await ctx.respond(f"Failed to add sound: {str(e)}")

    @discord.slash_command()
    @discord.default_permissions(manage_guild=True)
    async def edit_sound(
        self,
        ctx: discord.ApplicationContext,
        sound_name: str,
        new_name: str | None = None,
        new_emoji: str | None = None,
        new_volume: float | None = None,
    ):
        """Edits an existing sound in the guild's soundboard."""
        await ctx.defer()

        # Find the sound by name
        sounds = await ctx.guild.fetch_sounds()
        sound = discord.utils.get(sounds, name=sound_name)

        if not sound:
            return await ctx.respond(f"Sound '{sound_name}' not found!")

        try:
            await sound.edit(
                name=new_name or sound.name,
                emoji=(
                    discord.PartialEmoji.from_str(new_emoji)
                    if new_emoji
                    else sound.emoji
                ),
                volume=new_volume or sound.volume,
            )
            await ctx.respond(f"Updated sound: {sound.emoji} {sound.name}")
        except Exception as e:
            await ctx.respond(f"Failed to edit sound: {str(e)}")

    @discord.slash_command()
    async def play_sound(
        self,
        ctx: discord.ApplicationContext,
        sound_name: str,
        channel: discord.VoiceChannel | None = None,
    ):
        """Plays a sound in a voice channel."""
        await ctx.defer()

        # Use author's voice channel if none specified
        if not channel and ctx.author.voice:
            channel = ctx.author.voice.channel
        if not channel:
            return await ctx.respond("Please specify a voice channel or join one!")

        try:
            # Find the sound
            sounds = await ctx.guild.fetch_sounds()
            sound = discord.utils.get(sounds, name=sound_name)
            if not sound:
                # Check default sounds if not found in guild sounds
                defaults = await self.bot.fetch_default_sounds()
                sound = discord.utils.get(defaults, name=sound_name)

            if not sound:
                return await ctx.respond(f"Sound '{sound_name}' not found!")

            # Connect to voice channel if not already connected
            voice_client = await channel.connect()

            # Play the sound
            await channel.send_soundboard_sound(sound)
            await ctx.respond(f"Playing sound: {sound.emoji} {sound.name}")

            await asyncio.sleep(6)
            if voice_client.is_connected():
                await voice_client.disconnect()

        except Exception as e:
            await ctx.respond(f"Failed to play sound: {str(e)}")


bot.add_cog(SoundboardCog(bot))

bot.run(TOKEN)
