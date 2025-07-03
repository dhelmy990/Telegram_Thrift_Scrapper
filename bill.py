from telethon import TelegramClient, events
from config.secrets import t_api, t_hash, channel_username, mailing_cost, test_id, bill_text
from collections import defaultdict
from telethon.tl.types import InputMessagesFilterPhotos
from telethon.errors.rpcerrorlist import MsgIdInvalidError
from utils.collect_utils import last_used, save_time, iter_specific_messages, dt_min, save_pickle, load_pickle, load_whole_pickles_jar, delete_pickle
from utils.Auction import *
import db
import json
import os
import sys
import joblib
from datetime import timedelta
from client import client

async def gather_posts(since = None) -> dict[int, Post]:
    """
        If given a certain last used time, this function can gather all image collections with 'sb' in the text.
    """

    if since is not None:
        since = last_used()#change this to the time you want to gather auctions from
        iterator = client.iter_messages(channel_username, filter = InputMessagesFilterPhotos())
    else:
        since = dt_min()
        all_pkls = load_whole_pickles_jar('jar', 0) #this returns a list of lists. Even in the singleton case
        all_pkls = all_pkls[0]

        roots = []
        
        for pkl in all_pkls:
            if pkl[0] is None:
                roots.append(pkl[1].get_root())
            else:
                for post in pkl[1]:
                    roots.append(post.get_root())
                    

        iterator = iter_specific_messages(client, channel_username, message_ids = roots) 

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
    
    no_buy  = []
    have_buy = []
     
    id_purchases_dict = defaultdict(list) #k,v is tele_id,relevant_post. So are simply reformatting to go from the buyers to their post 
    
    for post in post_dict.values(): 
        try: 
            await post.gavel(channel_username, client)
        except(MsgIdInvalidError): #this is an edge case that occurs if the readme.md is not followed carefully and comments are turned off
            #TODO if this error occurs, simply delete. For now i don't really want to think about this yet
            continue
        except(KeyError): #theres no best buyer
            no_buy.append(post)
            continue

        have_buy.append(post)
        id_purchases_dict[post.best_buyer].append(post)
            
             
        if debug:
            print('--'*20)
            print(type(post), post.best_buyer)
            print(post.get_text())
            print("Original Price:", post.get_original_price())
            print("Current best:", post.offer)
            print("Offered by:", await post.get_best_buyer()), 
            print('--'*20)
            #also use post.get_all_images()

    return id_purchases_dict, have_buy, no_buy
    

async def send_order(buyer_to_post : tuple[int, list[Post]]):
    await client.start()
    id = test_id
    working_total = mailing_cost

    for post in buyer_to_post[1]:
        working_total += post.offer
        await client.send_file(id, post.get_all_images(), caption = str(post.offer))
    
    await client.send_message(id, bill_text.format(working_total))

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="CLI input handler")
    parser.add_argument("process_name", type=str, help="Name of the process") # i thought the 
    parser.add_argument('--user_id', type=int, 
                    help='for pkl finding and locating chat with client')
    parser.add_argument('--lookback', type=int, default=10, 
                    help='How far back to parse')
    

    # Parse the arguments
    args = parser.parse_args()
    process_name = args.process_name

    if process_name == 'active_orders':
        await active_posts()
    elif process_name == 'bill_customer':
        obj_id = args.user_id
        await send_order(load_pickle('1/' + str(obj_id)))
    elif process_name == 'scrape_chat':
        user = await client.get_entity(args.user_id)
        username = user.username 
        number = None
        #address = None
        async for message in client.iter_messages(args.user_id, limit = args.lookback, from_user = args.user_id):
            msg = message.text
            hp_no = r'\d{8}'
            postal = r'\d{6}'
            matches = re.findall(hp_no, msg)
            if matches and number is None:
                number = matches[0]
            matches = re.findall(postal, msg)
        print(username)
        print(number)
        #print(address)


    

    



# Test your Post objects


async def active_posts():
    #deal with the old first
    tasks = []
    OLD_post_dict = await gather_posts() #no param means get all the old ones
    buyer_to_post, have_bids, no_bids = await sieve_posts(OLD_post_dict, debug = False) #the latter two are lists of posts
    for post in have_bids:
        tasks.append(delete_pickle("0/" + str(post.get_root())))
    #remove those with bids
    
    #deal with the new now
    NEW_post_list = await gather_posts(since=last_used())
    more_buyer_to_post, have_bids, no_bids_2 = await sieve_posts(NEW_post_list, debug = False) #the latter two are lists of posts
    #add those with no bids. I called it no_bids_2 becasuse of the poster to seller UI problem.

    #well now we have bigger dict. Ahaha. Ha.
    union_keys = set(buyer_to_post.keys()) & set(more_buyer_to_post.keys())
    for key in union_keys:
        buyer_to_post[key].append(more_buyer_to_post.pop(key))
    buyer_to_post.update(more_buyer_to_post)
    no_bids += no_bids_2
    
    #Cache all images. This is a bad solution.

    """
        for posts in buyer_to_post.values():
            for post in posts:
                debug_pickle(post) 
        sys.exit(0)
    """

    for post in no_bids:
        tasks.append(post.fletify_image())
        tasks.append(save_pickle((None, post), "0/" + str(post.get_root())))
    for posts in buyer_to_post.items():
        tasks.append(save_pickle(posts, "0/" + str(posts[0])))
        for post in posts[1]:
            tasks.append(post.fletify_image())
            

    #save all of the above lmao
    #tasks.append(save_pickle(buyer_to_post, 'bought_dict'))
    #tasks.append(save_pickle(no_bids, 'unbought_dict'))
    await asyncio.gather(*tasks)
    #no bids comes later
    #return [(k, v) for k, v in buyer_to_post.items()] + [(None, post) for post in no_bids]
    

    #TODO of course, we still want to add the still_untouched_posts to a database
    #TODO await send_order(buyer_to_post), but maybe i dont call this from here sia...hm...

    
if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())

    
    


