import datetime

import discord

bot = discord.Bot()


@bot.command(guild_ids=[709325388592971866])
async def timeout(ctx, member: discord.Member, minutes: int):
    """Apply a timeout to a member"""

    duration = datetime.timedelta(minutes=minutes)
    await member.timeout_for(duration)
    await ctx.respond(f"Member timed out for {minutes} minutes.")

    """
    The method used above is a shortcut for

    until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
    await member.timeout(until)
    """


bot.run("TOKEN")
