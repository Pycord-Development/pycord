import discord

bot = discord.Bot()

# If you use commands.Bot, @bot.slash_command should be used for
# slash commands. You can use @bot.slash_command with discord.Bot aswell


@bot.command(guild_ids=[...])  # create a slash command for the supplied guilds
async def hello(ctx):
    """Say hello to the bot"""  # the command description can be supplied as the docstring
    await ctx.send(f"Hello {ctx.author}!")


@bot.command(
    name="hi"
)  # Not passing in guild_ids creates a global slash command (might take an hour to register)
async def global_command(ctx, num: int):  # Takes one integer parameter
    await ctx.send(f"This is a global command, {num}!")


@bot.command(guild_ids=[...])
async def joined(
    ctx, member: discord.Member = None
):  # Passing a default value makes the argument optional
    user = member or ctx.author
    await ctx.send(f"{user.name} joined at {discord.utils.format_dt(user.joined_at)}")

@bot.command(guild_ids=[...])
async def avatar(
    ctx,member : discord.Member = None
):
    if not member:
        member = ctx.author 
        
        # If no one is passed in for the member argument, it will make the author the member.   
    
    av = member.avatar.url

    embed = discord.Embed(title=f"{member}'s avatar",color = discord.Color.blurple())
    embed.set_image(url=av)
    await ctx.send(embed=embed)

    # This will send the mentioned user or the authors avatar in an embed!



# To learn how to add descriptions, choices to options check slash_options.py
bot.run("TOKEN")
