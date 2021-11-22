import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from aiohttp import ClientSession
from discord.commands import slash_command

async def getmeme():
    """
    using aiohttp for reddit random endpoint 
    """
    client = ClientSession()
    resp = await client.get("https://www.reddit.com/r/memes/random.json")
    resp = await resp.json()
    await client.close()
    return {
        "title":resp[0]["data"]["children"][0]["data"]["title"],
        "image":resp[0]["data"]["children"][0]["data"]["url_overridden_by_dest"],
        "permalink": f'https://www.reddit.com{resp[0]["data"]["children"][0]["data"]["permalink"]}'
    }

class memeNavigator(discord.ui.View):
    def __init__(self, ctx:Context=None):
        # making None is important if you want the button work after restart!
        super().__init__(timeout=None)
        self.ctx = ctx 

    #custom_id is required and should be unique
    @discord.ui.button(style=discord.ButtonStyle.blurple,emoji="◀️",custom_id="meme:leftButton")
    async def leftButton(self,button,interaction):
        try:
            self.ctx.pagenumber -=1
            resp = self.ctx.memearray[self.ctx.pagenumber]
            self.ctx.embed.description = f"[{resp['title']}]({resp['permalink']})"
            self.ctx.embed.set_image(url=resp["image"])
            await self.ctx.mememsg.edit_original_message(embed=self.ctx.embed)
        except:
            self.ctx.pagenumber +=1
            return

    #custom_id is required and should be unique
    @discord.ui.button(style=discord.ButtonStyle.blurple,emoji="▶️",custom_id="meme:rightButton")
    async def rightButton(self,button,interaction):
        try:
            self.ctx.pagenumber +=1
            resp = self.ctx.memearray[self.ctx.pagenumber]
            self.ctx.embed.description = f"[{resp['title']}]({resp['permalink']})"
            self.ctx.embed.set_image(url=resp["image"])
            await self.ctx.mememsg.edit_original_message(embed=self.ctx.embed)
            
        except:
            resp = await getmeme()
            self.ctx.embed.description = f"[{resp['title']}]({resp['permalink']})"
            self.ctx.embed.set_image(url=resp["image"])
            await self.ctx.mememsg.edit_original_message(embed=self.ctx.embed)
            self.ctx.memearray.append(resp)

    """
    timeout is used if there is a timeout on the button interaction with is None right now...
    
    async def on_timeout(self):
            for child in self.children:
                child.disabled = True
            await self.ctx.mememsg.edit_original_message(view=None)
    """

class MEME(commands.Cog):
    def __init__(self,client):
        self.client = client

    @slash_command(guild_ids=[...],name="meme",description="meme with slash and buttons!")
    async def meme(self,ctx):
        embed = discord.Embed(color=discord.Colour.dark_theme())
        ctx.embed = embed
        navigator = memeNavigator(ctx)
        resp = await getmeme()
        ctx.memearray = []
        ctx.memearray.append(resp)
        ctx.pagenumber = 0
        embed.description = f"[{resp['title']}]({resp['permalink']})"
        embed.set_image(url=resp["image"])
        mememsg = await ctx.respond(embed=embed,view=navigator)
        ctx.mememsg = mememsg

    @meme.error
    async def meme_error(self, ctx:Context ,error):
        return await ctx.respond(error,ephemeral=True) # ephemeral makes "Only you can see this" message

def setup(client):
    client.add_cog(MEME(client))