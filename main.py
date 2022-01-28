import discord
intents = discord.Intents.all()


bot = discord.Bot(debug_guilds=[911706065836605471])
extensions = ['ext', 'ext2']
for extension in extensions:
    bot.load_extension(extension)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print(bot.application_commands)
    print(bot._application_commands)

bot.run("OTMyNDY2OTc4NjcxNjkzODk1.YeTZjA.p4y7vE2Kw0uOC_WxPB-KO_G6VII")
