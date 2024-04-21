import discord

# debug_guilds must not be set if we want to set contexts and integration_types on commands
bot = discord.Bot()


@bot.slash_command(
    # Can only be used in private messages
    contexts={discord.InteractionContextType.private_channel},
    # Can only be used if the bot is installed to your user account,
    # if left blank it can only be used when added to guilds
    integration_types={discord.IntegrationType.user_install},
)
async def greet(ctx: discord.ApplicationContext, user: discord.User):
    await ctx.respond(f"Hello, {user}!")


@bot.slash_command(
    # This command can be used by guild members, but also by users anywhere if they install it
    integration_types={
        discord.IntegrationType.guild_install,
        discord.IntegrationType.user_install,
    },
)
async def say_hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hello!")


"""
If a bot is not installed to a guild and the guild has more than 25 members,
the response will always be ephemeral.

This is a Discord limitation and is subject to change.
"""


bot.run("TOKEN")