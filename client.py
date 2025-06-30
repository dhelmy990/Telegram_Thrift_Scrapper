from telethon import TelegramClient, events

from config.secrets import t_api, t_hash, channel_username, mailing_cost, test_id, bill_text


api_id = t_api           # int
api_hash = t_hash     # str
save_dir = 'media'  # Directory to save downloaded files
client = TelegramClient('anon_session', api_id, api_hash)

async def get_username(id : int):
    user = await client.get_entity(id)
    val = user.username
    return val if val is not None else "[BUYER DID NOT SET]"