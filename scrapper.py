from telethon import TelegramClient, events
from config.secrets import t_api, t_hash, channel_username

from telethon import TelegramClient, events
import json
import os

api_id = t_api           # int
api_hash = t_hash     # str
save_dir = 'media'  # Directory to save downloaded files

client = TelegramClient('anon_session', api_id, api_hash)

async def main():
    await client.start()
    
    # Get latest message
    messages = await client.get_messages(channel_username, limit=7)
    
    if messages:
        for msg in messages:
            if msg.media is not None:
                os.makedirs(save_dir, exist_ok=True)
                file_path = await msg.download_media(file=save_dir)
    else:
        print("No messages found.")

with client:
    client.loop.run_until_complete(main())
