import discord

bot = discord.Bot()


@bot.slash_command()
@discord.default_permissions(
    administrator=True
)  # only members with this permission can use this command
async def admin_only(ctx):
    await ctx.respond(f"Hello {ctx.author}, you are an administrator.")


@bot.slash_command()
@discord.default_permissions(
    manage_messages=True, ban_members=True
)  # you can supply multiple permissions
async def staff_only(ctx):
    await ctx.respond(f"Hello {ctx.author}, you can manage messages and ban members.")


"""
Server owners and administrators have all permissions and can change required permissions per-server.
If the member viewing commands does not have the required permissions, the commands will show up disabled.
"""


bot.run("TOKEN")
