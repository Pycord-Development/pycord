import discord
from discord import Option

bot = discord.Bot()


@bot.event
async def on_ready():
    print("Ready")

@bot.slash_command(description="Change the slowmode in a channel")
async def slowmode(ctx,
               channel: Option(discord.SlashCommandOptionType.channel, required=True,
                               channel_types=[discord.ChannelType.text],
                               description="In which Channel do you want to update the slowmode?"),
               time: Option(str, choices=["Off", "5s", "10s", "15s", "30s", "1m", "2m", "5m", "10m", "15m", "30m", "1h", "2h", "6h"],
                            description="How long should the slowmode be?")
               ):

        if "Off" in time:
            await channel.edit(slowmode_delay=0)
        if "5s" in time:
            await channel.edit(slowmode_delay=5)
        if "10s" in time:
            await channel.edit(slowmode_delay=10)
        if "15s" in time:
            await channel.edit(slowmode_delay=15)
        if "30s" in time:
            await channel.edit(slowmode_delay=30)
        if "1m" in time:
            await channel.edit(slowmode_delay=60)
        if "2m" in time:
            await channel.edit(slowmode_delay=120)
        if "5m" in time:
            await channel.edit(slowmode_delay=300)
        if "10m" in time:
            await channel.edit(slowmode_delay=600)
        if "15m" in time:
            await channel.edit(slowmode_delay=900)
        if "30m" in time:
            await channel.edit(slowmode_delay=1800)
        if "1h" in time:
            await channel.edit(slowmode_delay=3600)
        if "2h" in time:
            await channel.edit(slowmode_delay=7200)
        if "6h" in time:
            await channel.edit(slowmode_delay=21600)
        embed = discord.Embed(title="Slowmode",
                                   description=f"⏰ {ctx.author.mention} has sucessfully Changed the slowmode in {channel.mention} to ``{time}``!",
                                   color=discord.Color.green(),
                                   timestamp=discord.utils.utcnow()
                                   )
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon)
        await ctx.respond(embed=embed, ephemeral=True)
        return await channel.send(embed=embed)

bot.run("TOKEN")
