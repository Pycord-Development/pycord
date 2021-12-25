import datetime

import discord

bot = discord.Bot()


@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int):
    """Set timeout on a member"""

    now = discord.utils.utcnow()  # get current time
    until = now + datetime.timedelta(minutes=minutes)  # add the duration
    await member.timeout(until=until)
    await ctx.respond(f"Member timed out for {minutes} minutes.")


bot.run("TOKEN")
