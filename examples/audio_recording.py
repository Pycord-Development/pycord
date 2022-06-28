import discord

bot = discord.Bot(debug_guilds=[...])
bot.connections = {}

ENCODING_CHOICES = {
    "mp3": discord.sinks.MP3Sink(),
    "wav": discord.sinks.WaveSink(),
    "pcm": discord.sinks.PCMSink(),
    "ogg": discord.sinks.OGGSink(),
    "mka": discord.sinks.MKASink(),
    "mkv": discord.sinks.MKVSink(),
    "mp4": discord.sinks.MP4Sink(),
    "m4a": discord.sinks.M4ASink(),
}


@bot.command()
@option("encoding", choices=ENCODING_CHOICES.keys())
async def start(ctx: ApplicationContext, encoding: str):
    """
    Record your voice!
    """
    voice = ctx.author.voice

    if not voice:
        return await ctx.respond("You're not in a vc right now")

    vc = await voice.channel.connect()
    bot.connections.update({ctx.guild.id: vc})

    sink = ENCODING_CHOICES.get(encoding)
    if sink is None:
        return await ctx.respond("Invalid encoding.")

    vc.start_recording(
        sink,
        finished_callback,
        ctx.channel,
    )

    await ctx.respond("The recording has started!")


async def finished_callback(sink, channel: discord.TextChannel, *args):
    recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
    await sink.vc.disconnect()
    files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]
    await channel.send(f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=files)


@bot.command()
async def stop(ctx: discord.ApplicationContext):
    """Stop recording."""
    if ctx.guild.id in bot.connections:
        vc = bot.connections[ctx.guild.id]
        vc.stop_recording()
        del bot.connections[ctx.guild.id]
        await ctx.delete()
    else:
        await ctx.respond("Not recording in this guild.")


bot.run("TOKEN")
