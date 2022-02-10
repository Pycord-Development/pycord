import os
import pycord
from pycord.commands import Option, ApplicationContext

bot = pycord.Bot(debug_guilds=[...])
bot.connections = {}


@bot.command()
async def start(ctx: ApplicationContext,
                encoding: Option(str, choices=["mp3", "wav", "pcm", "ogg", "mka", "mkv", "mp4", "m4a", ])):
    """
    Record your voice!
    """

    voice = ctx.author.voice

    if not voice:
        return await ctx.respond("You're not in a vc right now")

    vc = await voice.channel.connect()
    bot.connections.update({ctx.guild.id: vc})

    if encoding == "mp3":
        sink = pycord.sinks.MP3Sink()
    elif encoding == "wav":
        sink = pycord.sinks.WaveSink()
    elif encoding == "pcm":
        sink = pycord.sinks.PCMSink()
    elif encoding == "ogg":
        sink = pycord.sinks.OGGSink()
    elif encoding == "mka":
        sink = pycord.sinks.MKASink()
    elif encoding == "mkv":
        sink = pycord.sinks.MKVSink()
    elif encoding == "mp4":
        sink = pycord.sinks.MP4Sink()
    elif encoding == "m4a":
        sink = pycord.sinks.M4ASink()
    else:
        return await ctx.respond("Invalid encoding.")

    vc.start_recording(
        sink,
        finished_callback,
        ctx.channel,
    )

    await ctx.respond("The recording has started!")


async def finished_callback(sink, channel: pycord.TextChannel, *args):
    recorded_users = [
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    await sink.vc.disconnect()
    files = [pycord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]
    await channel.send(f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=files)


@bot.command()
async def stop(ctx):
    """
    Stop recording.
    """
    if ctx.guild.id in bot.connections:
        vc = bot.connections[ctx.guild.id]
        vc.stop_recording()
        del bot.connections[ctx.guild.id]
        await ctx.delete()
    else:
        await ctx.respond("Not recording in this guild.")


bot.run("TOKEN")
