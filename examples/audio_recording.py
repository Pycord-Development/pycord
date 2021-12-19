import os
import discord
from discord.commands import Option

bot = discord.Bot(debug_guilds=[...])
bot.connections = {}


@bot.command()
async def start(ctx, encoding: Option(str, choices=["mp3", "wav", "pcm"])):
    """
    Record your voice!
    """

    voice = ctx.author.voice

    if not voice:
        return await ctx.respond("You're not in a vc right now")

    vc = await voice.channel.connect()
    bot.connections.update({ctx.guild.id: vc})

    vc.start_recording(
        discord.Sink(encoding=encoding),
        finished_callback,
        ctx.channel,
    )
    
    await ctx.respond("The recording has started!")


async def finished_callback(sink, channel, *args):

    recorded_users = [
        f" <@{user_id}> ({os.path.split(audio.file)[1]}) "
        for user_id, audio in sink.audio_data.items()
    ]
    await sink.vc.disconnect()
    await channel.send(f"Finished! Recorded audio for {', '.join(recorded_users)}.")

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