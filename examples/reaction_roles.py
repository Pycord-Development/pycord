import discord

intents = discord.Intents.default()
intents.members = True  # < This may give you `read-only` warning, just ignore it.
# This intent requires "Server Members Intent" to be enabled at https://discord.com/developers


bot = discord.Bot(intents=intents)

role_message_id = (
    0  # ID of the message that can be reacted to for adding/removing a role.
)

emoji_to_role = {
    discord.PartialEmoji(
        name="🔴"
    ): 0,  # ID of the role associated with unicode emoji '🔴'.
    discord.PartialEmoji(
        name="🟡"
    ): 0,  # ID of the role associated with unicode emoji '🟡'.
    discord.PartialEmoji(
        name="green", id=0
    ): 0,  # ID of the role associated with a partial emoji's ID.
}


@bot.event
async def on_ready():
    print("Ready!")


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Gives a role based on a reaction emoji."""
    # Make sure that the message the user is reacting to is the one we care about.
    if payload.message_id != role_message_id:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        # Make sure we're still in the guild, and it's cached.
        return

    try:
        role_id = emoji_to_role[payload.emoji]
    except KeyError:
        # If the emoji isn't the one we care about then exit as well.
        return

    role = guild.get_role(role_id)
    if role is None:
        # Make sure the role still exists and is valid.
        return

    try:
        # Finally, add the role.
        await payload.member.add_roles(role)
    except discord.HTTPException:
        # If we want to do something in case of errors we'd do it here.
        pass


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    """Removes a role based on a reaction emoji."""
    # Make sure that the message the user is reacting to is the one we care about.
    if payload.message_id != role_message_id:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        # Make sure we're still in the guild, and it's cached.
        return

    try:
        role_id = emoji_to_role[payload.emoji]
    except KeyError:
        # If the emoji isn't the one we care about then exit as well.
        return

    role = guild.get_role(role_id)
    if role is None:
        # Make sure the role still exists and is valid.
        return

    # The payload for `on_raw_reaction_remove` does not provide `.member`
    # so we must get the member ourselves from the payload's `.user_id`.
    member = guild.get_member(payload.user_id)
    if member is None:
        # Make sure the member still exists and is valid.
        return

    try:
        # Finally, remove the role.
        await member.remove_roles(role)
    except discord.HTTPException:
        # If we want to do something in case of errors we'd do it here.
        pass


bot.run("TOKEN")
