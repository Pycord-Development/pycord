# Webhooks
The Guide To Using Webhooks In Pycord

<!--TODO: Expand-->

## A Basic Webhook

Down below is a example of a simple webhook
```py
from discord import Webhook, AsyncWebhookAdapter
import aiohttp

async def example_message():
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url('url-here', adapter=AsyncWebhookAdapter(session))
        await webhook.send('Hello!', username='example_webhook')
```