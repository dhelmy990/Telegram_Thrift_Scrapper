from telethon import TelegramClient, events
from config.secrets import t_api, t_hash, channel_username

from telethon import TelegramClient, events
from utils.collect_utils import last_used, save_time
import json
import os
import sys
from datetime import timedelta

api_id = t_api           # int
api_hash = t_hash     # str
save_dir = 'media'  # Directory to save downloaded files

client = TelegramClient('anon_session', api_id, api_hash)

async def main():
    await client.start()
    
    # Get latest message
    
    time = last_used() - timedelta(hours=4)
    async for msg in client.iter_messages(channel_username):
        if msg.date < time:
            break
        if msg.media is not None:
            os.makedirs(save_dir, exist_ok=True)
            file_path = await msg.download_media(file=save_dir) 

    #logic: we have to know from where to begin collecting messages, combine this with the list of clothes yet unsold (if they still exist)
    #collect all past a certain date and time  TODO implement last log in system as well as unsold system 


    #(of new messages, be sure to filter out which ones are actually bids or not)

    #in each session, the system should also prompt for sellers who have NOT paid.
    #so then there's the people behind those sellers, and we should bill them. Unless those guys haven't paid either. 
    #In which case we have to skip them. As it turns out, there may actually be no one to sell to, so these messages ought to be
    #stored in the system

    #we will need to create an object, this object's job would be to contain all offers connected to a piece of clothing.
    #of course, it should contain these prices as a stack. basic leetcode problem. just store the ids of the persons who pay
    #from each of those objects, i would want to call a function that can automatically bill the top buyer, removing it from the stack
    #each buyer, per run, accrues a certain amount of money, and there's the image of the clothes associated with that. store as a tuple in a dict
    #from the dict we want to enumerate through, bill them for each item
    # at the end of this, i need to validate how many of these people actually paid. So i need to figure out a relatively simple way
    # to allow wanxuan to bill the next person, should the payment fail.



with client:
    client.loop.run_until_complete(main())