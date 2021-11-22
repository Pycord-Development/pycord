import discord
from discord.commands.commands import Option, SlashCommandGroup
from discord.ext import commands
from discord.ext.commands.context import Context

class MATH(commands.Cog):
    def __init__(self, client):
        self.client = client
        moderation = SlashCommandGroup("moderation", "Commands related to moderation.")

        @moderation.command(guild_ids=[...],description="kick some people")
        async def kick(self, ctx:Context,
                       member:Option(discord.Member),
                       reason:Option(str,description="reason")
                    ):
            if ctx.author.guild_permissions.kick_members == True:
                await member.kick(reason=reason)
                await ctx.respond("hello")
            else:
                await ctx.respond("you dont have the permission to do so!",ephemeral=True)
        
        @moderation.command(guild_ids=[...],description="ban some people")
        async def ban(self, ctx:Context,
                      member:Option(discord.Member),
                      reason:Option(str,description="reason")
                    ):
            if ctx.author.guild_permissions.ban_members == True:
                await member.ban(reason=reason)
                await ctx.respond("done")
            else:
                await ctx.respond("you dont have the permission to do so!",ephemeral=True)
        
        client.add_application_command(moderation)

def setup(client):
    client.add_cog(MATH(client))
