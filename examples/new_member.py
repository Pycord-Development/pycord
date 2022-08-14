import discord

intents = discord.Intents.default()
intents.members = True  # This intent requires "Server Member Intent" to be enabled at https://discord.com/developers
# ^ This may give you `read-only` warning, just ignore it.

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print('Ready!')


@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    if guild.system_channel is not None:  # For this to work, System Messages Channel should be set in guild settings.
        await guild.system_channel.send(f"Welcome {member.mention} to {guild.name}!")


bot.run("TOKEN")
