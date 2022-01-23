import discord
from discord.commands.commands import Option, SlashCommandGroup
from discord.ext import commands
from discord.ext.commands.context import Context


class SlashGroupExample(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # <discord.commands.commands.SlashCommandGroup>
        moderation = SlashCommandGroup("moderation", "Commands related to moderation.")

        @moderation.command(guild_ids=[...], description="kick some people")
        async def kick(
            self,
            ctx: Context,
            member: Option(discord.Member),
            reason: Option(str, description="reason"),
        ):

            # check kick members permission for the author
            if ctx.author.guild_permissions.kick_members == True:
                # https://docs.pycord.dev/en/master/api.html#discord.Member.kick
                await member.kick(reason=reason)
                await ctx.respond("hello")
            else:

                await ctx.respond(
                    "you dont have the permission to do so!", ephemeral=True
                )

        @moderation.command(guild_ids=[...], description="ban some people")
        async def ban(
            self,
            ctx: Context,
            member: Option(discord.Member),
            reason: Option(str, description="reason"),
        ):

            # check ban members permission for the author
            if ctx.author.guild_permissions.ban_members == True:
                # https://docs.pycord.dev/en/master/api.html#discord.Member.ban
                await member.ban(reason=reason)
                await ctx.respond("done")
            else:
                await ctx.respond(
                    "you dont have the permission to do so!", ephemeral=True
                )

        # Adds the application command
        bot.add_application_command(moderation)


def setup(bot):
    bot.add_cog(SlashGroupExample(bot))
