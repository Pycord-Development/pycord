import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

positive_emoji: str = "\U00002705"
negative_emoji: str = "\U0000274e"

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=intents
)


# return True if channel was thread.
def is_thread(ctx: commands.Context) -> bool:
    return isinstance(ctx.channel, discord.Thread)


@bot.event
async def on_ready():
    print(f"Logged in {bot.user.name} (ID: {bot.user.id})")
    print("------")


@bot.command(name="archive")
@commands.guild_only()
@commands.bot_has_permissions(manage_threads=True)
@commands.check(is_thread)
async def thread_archive(ctx: commands.Context):
    # add success reaction.
    await ctx.message.add_reaction(positive_emoji)
    # close Thread.
    await ctx.channel.archive()


#  When `archive` command fails.
@thread_archive.error
async def archive_error(ctx: commands.Context, error: discord.DiscordException):
    # React to that message.
    await ctx.message.add_reaction(negative_emoji)

    # Occurs when the bot does not have permission to manage threads.
    # This error occurs `bot_has_permissions` decorator.
    if isinstance(error, commands.BotMissingPermissions):
        return await ctx.send("Missing `manage_threads` permission")

    # Occurs when the channel is not a guild channel.
    # This error occurs `guild_only` decorator.
    if isinstance(error, commands.NoPrivateMessage):
        return await ctx.send("This command can use only guilds")

    # Occurs when is_thread function returns false. (the channel is not a thread)
    # This error occurs `check(is_thread)` decorator.
    # (occurs when the original check decorator is created and an error occurs there.)
    if isinstance(error, commands.CheckFailure):
        return await ctx.send("This channel is not thread!")


bot.run("TOKEN")
