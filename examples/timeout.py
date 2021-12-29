import discord
from discord import client
from discord.ext import commands, tasks
import datetime
from datetime import datetime, timedelta

bot = commands.Bot(command_prefix="$")

@bot.event
async def on_ready():
    print(f"Bot is logged in as {bot.user} ({bot.user.id})")

def convertduration(time):
    pos = ["m", "h", "d"]
    time_dict = {"m": 60, "h": 3600, "d": 3600 * 24}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]

@commands.has_permissions(moderate_members=True)
@commands.bot_has_permissions(moderate_members=True)
@bot.command()
async def timeout(ctx, member: discord.Member=None, duration=None, *, reason=None):
    if member is None and duration is None:
        return await ctx.send("Command usage: ``$timeout @member/id duration reason(optional)``")
    if reason is None:
        reason = "No reason provided"
    if member.communication_disabled_until is not None:
        return await ctx.send("This Member is already timeouted.")
    if member == ctx.author:
        return await ctx.send("You can`t timeout yourself!")
    now = datetime.utcnow()
    time = convert(duration)
    if time == -1:
        await ctx.send(f'The given duration is not valid!')
        return
    if res == -2:
        await ctx.send(f'Something went wrong converting the time.')
        return
    timeout_until = now + timedelta(seconds=time)
    try:
        await member.timeout(until=timeout_until, reason=reason)
    except:
        return await ctx.send("Something went wrong while timeouting the member. Check the command usage/duration etc.")
    await ctx.send(f"The member ``{member}`` recieved a timeout until <t:{int(timeout_until.timestamp())}> for:\n``{reason}``.")

@commands.has_permissions(moderate_members=True)
@commands.bot_has_permissions(moderate_members=True)
@bot.command()
async def removetimeout(ctx, member: discord.Member=None, *, reason=None):
    if member is None:
        return await ctx.send("Command usage: ``$removetimeout @member/id reason(optional)``")
    if reason is None:
        reason = "No reason provided"
    if member.communication_disabled_until is None:
        return await ctx.send("This Member is not timeouted yet.")
    try:
        await member.remove_timeout(reason=reason)
    except:
        return await ctx.send("Something went wrong while removing the timeout! Check the command usage.")
    await ctx.send(f"The member timeout is now removed from ``{member}``.")

bot.run("token")
