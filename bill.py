from telethon import TelegramClient, events
from config.secrets import t_api, t_hash, channel_username, mailing_cost, test_id, bill_text
from collections import defaultdict
from telethon.tl.types import InputMessagesFilterPhotos
from telethon.errors.rpcerrorlist import MsgIdInvalidError
from utils.collect_utils import last_used, save_time, iter_specific_messages, dt_min
from utils.Auction import *
import db
import json
import os
import sys
from datetime import timedelta
from client import client

async def gather_posts(since = None) -> dict[int, Post]:
    """
        If given a certain last used time, this function can gather all image collections with 'sb' in the text.
    """

    if since is not None:
        since = since - timedelta(hours=120) #change this to the time you want to gather auctions from
        iterator = client.iter_messages(channel_username, filter = InputMessagesFilterPhotos())
    else:
        since = dt_min()
        db.init_undone_bid()
        iterator = iter_specific_messages(client, channel_username, message_ids = db.get_all_ORDERED()) 

    posts = {} 
    cluster = [] #of working images

    async for msg in iterator:
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

async def sieve_posts(post_dict: dict[int, Post], debug = False):
    """
        3 items returned, in this order
        1. A dict with keys of buyer id, and a List of the posts they purchased as the value
        2. A list of posts of those newly purchased
        3. A list of posts of those that still remain unpurchased

        (Internal logic)
        For each post, we are finding the best buyer and updating their internal representations
        As a return type, it must also have the responsibility of returning posts which contain no poster
    """
    await client.start()
    
    no_buy  = []
    have_buy = []
     
    id_purchases_dict = defaultdict(lambda : list()) #k,v is tele_id,relevant_post. So are simply reformatting to go from the buyers to their post 
    
    for post in post_dict.values():
        print('--'*20)
        try: 
            await post.gavel(channel_username, client)
        except(MsgIdInvalidError): #this is an edge case that occurs if the readme.md is not followed carefully and comments are turned off
            #TODO if this error occurs, simply delete. For now i don't really want to think about this yet
            continue

        if not post.offer_ready():
            no_buy.append(post)
            continue
        else:
            have_buy.append(post)
            id_purchases_dict[post.best_buyer].append(post)
            
             
        if debug:
            print(type(post), post.best_buyer)
            print(post.get_text())
            print("Original Price:", post.get_original_price())
            print("Current best:", post.offer)
            print("Offered by:", await post.get_best_buyer()), 
            print('--'*20)
            #also use post.get_all_images()

    return id_purchases_dict, have_buy, no_buy
    

async def send_order(buyer_to_post : dict[int, Post]):
    for id, list_of_posts in buyer_to_post.items():
        id = test_id
        working_total = mailing_cost

        for post in list_of_posts:
            working_total += post.offer
            await client.send_file('me', post.get_all_images(), caption = str(post.offer))
        
        await client.send_message(id, bill_text.format(working_total))

async def main():
    """
        I AM USING THIS AS A DEBUG FUNCTION. ACTUAL UTILITY FUNCTION IS BELOW.
    """
    await client.start()

    #deal with the old first
    OLD_post_dict = await gather_posts() #no param means get all the old ones
    buyer_to_post , have_bids, no_bids = await sieve_posts(OLD_post_dict, debug = True) #the latter two are lists of posts
    #remove those with bids
    
    #deal with the new now
    NEW_post_list = await gather_posts(since=last_used())
    more_buyer_to_post , have_bids, no_bids = await sieve_posts(NEW_post_list, debug = True) #the latter two are lists of posts
    #add those with no bids

    #well now we have bigger dict. Ahaha. Ha.
    buyer_to_post.update(more_buyer_to_post)

    #TODO of course, we still want to add the still_untouched_posts to a database

    await send_order(buyer_to_post)

async def active_posts():
    await client.start()

    #deal with the old first
    OLD_post_dict = await gather_posts() #no param means get all the old ones
    buyer_to_post , have_bids, no_bids = await sieve_posts(OLD_post_dict, debug = True) #the latter two are lists of posts
    #remove those with bids
    
    #deal with the new now
    NEW_post_list = await gather_posts(since=last_used())
    more_buyer_to_post , have_bids, no_bids_2 = await sieve_posts(NEW_post_list, debug = True) #the latter two are lists of posts
    #add those with no bids. I called it no_bids_2 becasuse of the poster to seller UI problem.

    #well now we have bigger dict. Ahaha. Ha.
    buyer_to_post.update(more_buyer_to_post)
    return buyer_to_post, no_bids + no_bids_2

    #TODO of course, we still want to add the still_untouched_posts to a database
    #TODO await send_order(buyer_to_post), but maybe i dont call this from here sia...hm...

    
if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())

    
    


