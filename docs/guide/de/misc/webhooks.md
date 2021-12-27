# Webhooks
Die Anleitung zur Verwendung von Webhooks in Pycord

## Ein einfacher Webhook

Nachfolgend ein Beispiel für einen einfachen Webhook
Pycord
```py
from discord importieren Webhook, AsyncWebhookAdapter
import aiohttp

async def beispiel_nachricht():
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url('url-here', adapter=AsyncWebhookAdapter(session))
        await webhook.send('Hallo!', username='example_webhook')
```