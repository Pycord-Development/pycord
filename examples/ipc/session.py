from sanic import Sanic
from discord.ext import ipc

app = Sanic(__name__)
session = ipc.Session("localhost", 20000, "my_secret_token")

@app.route("/")
async def get_members():
    count = await session.request("get_member_count", guild_id=881207955029110855) # request the member count from the Server instance.
    print(count) # print the count.

app.run()
