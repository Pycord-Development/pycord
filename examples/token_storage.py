# This example will show you how to share your main bot code safely, without compromising your token.
# However, always keep your token safe, no matter where it is stored. Never EVER give access to your token to anyone else.

# Before following these steps, you will have to install a library called "python-dotenv" via pip, like so:
"""
pip install python-dotenv
"""

# Now, you must add a file to your bot's root directory called ".env".

# Inside this file, write the following, without the """s.

"""
DISCORD_TOKEN = {your_bot_token_here}
"""

# Save the file before moving back to your code.

# Then, you need to import "os", which allows Python to access the Operating System or Server it is being used on, like so:

"""
import os
"""

# You do not need to install os via pip, as the os module is installed with Python 3.

# Then, you need to import "dotenv", and its function "load_dotenv", not "python-dotenv", like so:

"""
import dotenv
from dotenv import load_dotenv
"""

# Then, add these lines to your code.

"""
load_dotenv('.env')
token = os.getenv("DISCORD_TOKEN")
"""

# Then, edit your bot.run to use the token variable, instead of your actual token.

# The final result should look something like this:

"""
import os
import dotenv
from dotenv import load_dotenv
import discord

bot = discord.Bot()
load_dotenv('.env')

token = os.getenv("DISCORD_TOKEN")
bot.run(token)
"""


