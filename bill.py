from telethon import TelegramClient, events
from config.secrets import t_api, t_hash, channel_username
from telethon.tl.types import InputMessagesFilterPhotos
from telethon.errors.rpcerrorlist import MsgIdInvalidError
from utils.collect_utils import last_used, save_time
from utils.Auction import *
import json
import os
import sys
from datetime import timedelta

api_id = t_api           # int
api_hash = t_hash     # str
save_dir = 'media'  # Directory to save downloaded files

client = TelegramClient('anon_session', api_id, api_hash)

async def gather_posts(since) -> list[Post]:
    """
        If given a certain last used time, this function can gather all image collections with 'sb' in the text.
    """

    #TODO TOGGLE THIS OFF LATER:
    since = since - timedelta(hours=40) #change this to the time you want to gather auctions from

    posts = [] #
    cluster = [] #of working images

    async for msg in client.iter_messages(channel_username, filter = InputMessagesFilterPhotos()):
        #if msg.date < since:
            #break

        cluster.append(msg)
        if msg.text is not None:
            res = Post.Factory(msg, cluster)
            if res is None: continue
            posts.append(res)

    return posts

async def close_posts(post_list: list[Post]):
    await client.start()
    #debug lines
    for post in post_list:
        print('--'*20)
        try: 
            id, cost = await post.gavel(channel_username, client)
        except(MsgIdInvalidError):
            continue

        print(type(post), id)
        print(post.get_text())
        print("Original Price:", post.get_original_price())
        print("Current best:", cost)
        print
        print('--'*20)
         
        

async def main():
    await client.start()
    post_list = await gather_posts(since=last_used())
    await close_posts(post_list)
    

    

with client:
    client.loop.run_until_complete(main())