# This example requires the 'members' privileged intents

import pycord


class MyClient(pycord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.role_message_id = (
            0  # ID of the message that can be reacted to to add/remove a role.
        )
        self.emoji_to_role = {
            pycord.PartialEmoji(
                name="🔴"
            ): 0,  # ID of the role associated with unicode emoji '🔴'.
            pycord.PartialEmoji(
                name="🟡"
            ): 0,  # ID of the role associated with unicode emoji '🟡'.
            pycord.PartialEmoji(
                name="green", id=0
            ): 0,  # ID of the role associated with a partial emoji's ID.
        }

    async def on_raw_reaction_add(self, payload: pycord.RawReactionActionEvent):
        """Gives a role based on a reaction emoji."""
        # Make sure that the message the user is reacting to is the one we care about.
        if payload.message_id != self.role_message_id:
            return

        guild = self.get_guild(payload.guild_id)
        if guild is None:
            # Check if we're still in the guild and it's cached.
            return

        try:
            role_id = self.emoji_to_role[payload.emoji]
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
        except pycord.HTTPException:
            # If we want to do something in case of errors we'd do it here.
            pass

    async def on_raw_reaction_remove(self, payload: pycord.RawReactionActionEvent):
        """Removes a role based on a reaction emoji."""
        # Make sure that the message the user is reacting to is the one we care about.
        if payload.message_id != self.role_message_id:
            return

        guild = self.get_guild(payload.guild_id)
        if guild is None:
            # Check if we're still in the guild and it's cached.
            return

        try:
            role_id = self.emoji_to_role[payload.emoji]
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
        except pycord.HTTPException:
            # If we want to do something in case of errors we'd do it here.
            pass


intents = pycord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
client.run("token")
