from __future__ import annotations

import asyncio
import logging
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import discord
from discord.ext import commands

TOKEN_ENV = "PYCORD_TOKEN"
PREFIX_ENV = "PYCORD_PREFIX"
LOG_DIR_ENV = "VOICE_TEST_LOG_DIR"
DEBUG_ENV = "VOICE_DEBUG"
FFMPEG_ENV = "PYCORD_FFMPEG_PATH"
RECORDINGS_DIR_ENV = "VOICE_RECORDINGS_DIR"


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def configure_logging() -> Path:
    log_dir = Path(os.getenv(LOG_DIR_ENV, "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"voice-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"

    debug_enabled = _as_bool(os.getenv(DEBUG_ENV), True)
    level = logging.DEBUG if debug_enabled else logging.INFO
    formatter = logging.Formatter(
        "[%(asctime)s %(levelname)s] %(name)s - %(message)s", "%H:%M:%S"
    )

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    root.addHandler(file_handler)
    root.addHandler(console_handler)
    logging.getLogger("discord.http").setLevel(logging.INFO)

    return log_file


def resolve_voice_channel(
    ctx: commands.Context, channel: discord.VoiceChannel | None
) -> discord.VoiceChannel | None:
    if channel is not None:
        return channel
    author_voice = getattr(ctx.author, "voice", None)
    if author_voice and author_voice.channel:
        return author_voice.channel
    return None


def summarize_dave(vc: discord.VoiceClient) -> str:
    state = vc._connection
    session = state.dave_session

    parts = [
        f"mode={state.mode}",
        f"proto={state.dave_protocol_version}",
        f"pending_transition={state.dave_pending_transition}",
        f"downgraded={state.downgraded_dave}",
    ]

    if session is None:
        parts.append("session=None")
        return " | ".join(parts)

    try:
        user_ids = session.get_user_ids()
    except Exception:
        user_ids = []

    parts.extend(
        [
            f"session.ready={getattr(session, 'ready', None)}",
            f"session.status={getattr(session, 'status', None)}",
            f"session.epoch={getattr(session, 'epoch', None)}",
            f"session.users={user_ids}",
            f"privacy_code={getattr(session, 'voice_privacy_code', None)}",
        ]
    )
    return " | ".join(parts)


def _recording_key_to_filename(key: Any) -> str:
    if isinstance(key, int):
        return str(key)

    key_id = getattr(key, "id", None)
    if isinstance(key_id, int):
        return str(key_id)

    raw = str(key)
    safe = "".join(ch for ch in raw if ch.isalnum() or ch in ("-", "_", "."))
    return safe or "unknown"


async def recording_finished_callback(
    sink: discord.sinks.Sink, channel: discord.abc.Messageable, started_by: int
) -> None:
    base_dir = Path(os.getenv(RECORDINGS_DIR_ENV, str(REPO_ROOT / "recordings")))
    out_dir = base_dir / datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for user_id, audio in sink.audio_data.items():
        out_name = _recording_key_to_filename(user_id)
        out_path = out_dir / f"{out_name}.{sink.encoding}"
        audio.file.seek(0)
        out_path.write_bytes(audio.file.read())
        saved.append(out_path.name)

    await channel.send(
        f"Recording finished. files={len(saved)}, encoding={sink.encoding}, "
        f"started_by=<@{started_by}>, dir=`{out_dir.resolve()}`"
    )


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix=os.getenv(PREFIX_ENV, "!"),
    intents=intents,
    help_command=commands.DefaultHelpCommand(no_category="Commands"),
)

log = logging.getLogger("voice-test")


@bot.event
async def on_ready() -> None:
    log.info("ready as %s (%s)", bot.user, bot.user and bot.user.id)


@bot.event
async def on_member_speaking_state_update(
    member: discord.Member, ssrc: int, speaking_state: Any
) -> None:
    log.info("speaking-state member=%s ssrc=%s state=%s", member.id, ssrc, speaking_state)


@bot.event
async def on_member_speaking_start(member: discord.Member) -> None:
    log.info("speaking-start member=%s", member.id)


@bot.event
async def on_member_speaking_stop(member: discord.Member) -> None:
    log.info("speaking-stop member=%s", member.id)


@bot.command()
async def ping(ctx: commands.Context) -> None:
    await ctx.send("pong")


@bot.command()
async def join(ctx: commands.Context, *, channel: discord.VoiceChannel | None = None) -> None:
    target = resolve_voice_channel(ctx, channel)
    if target is None:
        await ctx.send("No target voice channel. Join one or pass a channel.")
        return

    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(target)
        await ctx.send(f"Moved to {target.mention}")
        return

    vc = await target.connect()
    await ctx.send(f"Joined {target.mention}")
    log.info("voice joined guild=%s channel=%s %s", ctx.guild and ctx.guild.id, target.id, summarize_dave(vc))


@bot.command()
async def move(ctx: commands.Context, *, channel: discord.VoiceChannel) -> None:
    vc = ctx.voice_client
    if vc is None:
        await ctx.send("Not in voice.")
        return
    await vc.move_to(channel)
    await ctx.send(f"Moved to {channel.mention}")
    log.info("voice moved channel=%s %s", channel.id, summarize_dave(vc))


@bot.command()
async def leave(ctx: commands.Context) -> None:
    vc = ctx.voice_client
    if vc is None:
        await ctx.send("Not in voice.")
        return
    await vc.disconnect(force=True)
    await ctx.send("Left voice.")


@bot.command()
async def stop(ctx: commands.Context) -> None:
    vc = ctx.voice_client
    if vc is None:
        await ctx.send("Not in voice.")
        return
    if vc.is_playing():
        vc.stop()
        await ctx.send("Stopped playback.")
    else:
        await ctx.send("Not playing.")


@bot.command()
async def play(ctx: commands.Context, *, source: str) -> None:
    vc = ctx.voice_client
    if vc is None:
        target = resolve_voice_channel(ctx, None)
        if target is None:
            await ctx.send("Join voice first or use !join <channel>.")
            return
        vc = await target.connect()

    source_path = Path(source).expanduser()
    if not source_path.exists():
        await ctx.send(f"File not found: `{source_path}`")
        return

    ffmpeg_path = os.getenv(FFMPEG_ENV)
    audio = (
        discord.FFmpegPCMAudio(str(source_path), executable=ffmpeg_path)
        if ffmpeg_path
        else discord.FFmpegPCMAudio(str(source_path))
    )

    if vc.is_playing():
        vc.stop()

    def after_play(err: Exception | None) -> None:
        if err:
            log.exception("playback error", exc_info=err)
        else:
            log.info("playback finished source=%s", source_path)

    vc.play(audio, after=after_play)
    await ctx.send(f"Playing `{source_path.name}`")
    log.info("play start source=%s %s", source_path, summarize_dave(vc))


@bot.command(name="record_start")
async def record_start(ctx: commands.Context, encoding: str = "wav") -> None:
    vc = ctx.voice_client
    if vc is None:
        target = resolve_voice_channel(ctx, None)
        if target is None:
            await ctx.send("Join voice first or use !join <channel>.")
            return
        vc = await target.connect()

    if vc.is_recording():
        await ctx.send("Already recording.")
        return

    enc = encoding.lower().strip()
    sink_filters = {"fill_silence": True}
    sink_map: dict[str, discord.sinks.Sink] = {
        "wav": discord.sinks.WaveSink(filters=sink_filters),
        "mp3": discord.sinks.MP3Sink(filters=sink_filters),
        "pcm": discord.sinks.PCMSink(filters=sink_filters),
    }
    sink = sink_map.get(enc)
    if sink is None:
        await ctx.send("Unsupported encoding. Use wav/mp3/pcm.")
        return

    finish_once = threading.Event()

    def on_recording_finished(exc: Exception | None) -> None:
        if finish_once.is_set():
            return
        finish_once.set()
        if exc is not None:
            log.exception("recording finished with error", exc_info=exc)
        future = asyncio.run_coroutine_threadsafe(
            recording_finished_callback(sink, ctx.channel, ctx.author.id),
            bot.loop,
        )

        def on_callback_done(f: Any) -> None:
            callback_error = f.exception()
            if callback_error is not None:
                log.exception("recording callback failed", exc_info=callback_error)

        future.add_done_callback(on_callback_done)

    vc.start_recording(sink, on_recording_finished)
    await ctx.send(f"Recording started (`{enc}`).")
    log.info("recording started encoding=%s %s", enc, summarize_dave(vc))


@bot.command(name="record_stop")
async def record_stop(ctx: commands.Context) -> None:
    vc = ctx.voice_client
    if vc is None or not vc.is_recording():
        await ctx.send("Not recording.")
        return
    vc.stop_recording()
    await ctx.send("Recording stopped.")


@bot.command(name="dave")
async def dave(ctx: commands.Context) -> None:
    vc = ctx.voice_client
    if vc is None:
        await ctx.send("Not in voice.")
        return
    summary = summarize_dave(vc)
    await ctx.send(f"`{summary}`")
    log.info("dave status %s", summary)


@bot.command(name="ssrc")
async def ssrc(ctx: commands.Context) -> None:
    vc = ctx.voice_client
    if vc is None:
        await ctx.send("Not in voice.")
        return
    await ctx.send(f"`id_to_ssrc={vc._id_to_ssrc}`")


def main() -> None:
    log_file = configure_logging()
    token = os.getenv(TOKEN_ENV)
    if not token:
        raise RuntimeError(f"Missing env var {TOKEN_ENV}")
    discord_path = Path(getattr(discord, "__file__", "<unknown>")).resolve()
    log.info("discord import path=%s", discord_path)
    if "site-packages" in str(discord_path).lower():
        log.warning(
            "discord imported from site-packages; local repo code may not be active"
        )
    log.info("starting test bot, log_file=%s", log_file)
    bot.run(token)


if __name__ == "__main__":
    main()

