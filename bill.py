from telethon import TelegramClient, events
from config.secrets import t_api, t_hash, channel_username, mailing_cost, test_id, bill_text
from collections import defaultdict
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

async def gather_posts(since) -> dict[int, Post]:
    """
        If given a certain last used time, this function can gather all image collections with 'sb' in the text.
    """

    #TODO TOGGLE THIS OFF LATER:
    since = since - timedelta(hours=120) #change this to the time you want to gather auctions from

    posts = {} #
    cluster = [] #of working images

    async for msg in client.iter_messages(channel_username, filter = InputMessagesFilterPhotos()):
        if msg.date < since:
            break

        cluster.append(msg)
        if msg.text is not None:
            res = Post.Factory(msg, cluster)
            cluster = []
            if res is None: continue
            if posts.get(res.get_root) is not None:
                raise Exception #this would be a major problem..
            posts[res.get_root] = res

    return posts




async def gather_older_posts() -> dict[int, Post]:
    """
        Using a database, will simply fetch all of the posts from the past that have not gained any buyers
    """

    #TODO: later, you can comment out the below and implement
    #once we get to this part, claude suggests: message = await client.get_messages(chat_entity, ids=message_id)
    return {}


async def collate_posts(post_dict: dict[int, Post], debug = False):
    """
        For each post, we are finding the best buyer and updating their internal representations
        As a return type, it must also have the responsibility of returning posts which contain no poster
    """
    await client.start()
    

    new_unmarked_posts = [] #we use this as a list of ids
    id_purchases_dict = defaultdict(lambda : list()) #k,v is tele_id,relevant_post. So are simply reformatting to go from the buyers to their post 
    
    for post in post_dict.values():
        print('--'*20)
        try: 
            await post.gavel(channel_username, client)
        except(MsgIdInvalidError): #this is an edge case that occurs if the readme.md is not followed carefully and comments are turned off
            continue

        if not post.offer_ready():
            new_unmarked_posts.append(post)
            continue
        else:
            id_purchases_dict[post.best_buyer].append(post)
            
        if debug:
            print(type(post), post.best_buyer)
            print(post.get_text())
            print("Original Price:", post.get_original_price())
            print("Current best:", post.offer)
            print("Offered by:"), 
            print('--'*20)

    return id_purchases_dict, new_unmarked_posts
        

def some_db_func(post):
    pass




async def send_order(buyer_to_post : dict[int, Post]):
    for id, list_of_posts in buyer_to_post.items():
        id = test_id
        working_total = mailing_cost

        for post in list_of_posts:
            working_total += post.offer
            await client.send_file('me', post.get_all_images(), caption = str(post.offer))
        
        
        await client.send_message(id, bill_text.format(working_total))
        



async def main():
    await client.start()
    NEW_post_list = await gather_posts(since=last_used())
    OLD_post_list = await gather_older_posts()
    post_list = {**NEW_post_list, **OLD_post_list}
    

    #NOTE: the functions main purpose is to _____, but it also can return all posts that have yet to have been touched
    buyer_to_post , still_untouched_posts = await collate_posts(post_list, debug = True) 
    #TODO eventually, we add still_untouched_posts to add to a database
    await send_order(buyer_to_post)



    


    
    

    
    

    

with client:
    client.loop.run_until_complete(main())