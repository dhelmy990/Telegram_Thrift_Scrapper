from telethon import TelegramClient, events
from config.secrets import t_api, t_hash, channel_username
from telethon.tl.types import InputMessagesFilterPhotos
from utils.collect_utils import last_used, save_time
from utils.Auction import Auction
import json
import os
import sys
from datetime import timedelta

api_id = t_api           # int
api_hash = t_hash     # str
save_dir = 'media'  # Directory to save downloaded files

client = TelegramClient('anon_session', api_id, api_hash)

async def get_ori_id():
    auctions = [] #
    cluster = [] #of working images

    async for msg in client.iter_messages(
        channel_username,
        filter = InputMessagesFilterPhotos()):
        time = last_used() - timedelta(hours=40)
        
        if msg.date < time:
            break
        
        if msg.text is None:
            cluster.append(msg)
        elif 'sb' not in msg.text.lower():
            cluster = []
        else:
            cluster.append(msg)
            auctions.append(Auction(root = msg.id, items = cluster))
            cluster = [] 
           
    return auctions

async def main():
    await client.start()
    
    #i never thought leetcode would come in handy for this, but here we are

    for auction in await get_ori_id():
        async for reply in client.iter_messages(channel_username, reply_to=auction.get_root()):
            print(str(reply.sender_id) + "=>"  + reply.text) 
        print()

        

    

with client:
    client.loop.run_until_complete(main())