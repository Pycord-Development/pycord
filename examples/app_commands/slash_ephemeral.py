import discord


bot = discord.Bot()
# This can be commands.Bot


@bot.slash_command(name='hi')
async def ephemeral_message(ctx):
  await ctx.send("Hello, only you can see this message 🙂", ephemeral=True)
  
bot.run("...") # your token.
