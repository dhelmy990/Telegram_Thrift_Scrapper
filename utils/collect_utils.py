from datetime import datetime, timezone
import pytz


sgt_timezone = pytz.timezone('Asia/Singapore')

def save_time():
    with open('config/last_login.txt', 'w') as f:
        f.write(datetime.now().isoformat())

def last_used() -> datetime:
    # Read the timestamp
    try:
        with open('config/last_login.txt', 'r') as f:
            timestamp_str = f.read().strip()
            last_seen = datetime.fromisoformat(timestamp_str)
            
    except FileNotFoundError:
        save_time()
        last_seen = datetime.now()
    
    
    #save_time()
    return sgt_timezone.localize(last_seen)

def dt_min() -> datetime:
    return datetime.min.replace(tzinfo=timezone.utc).astimezone(sgt_timezone)
    
    


async def iter_specific_messages(client, entity, message_ids):
    """Custom async iterator for specific message IDs"""
    messages = await client.get_messages(entity, ids=message_ids)
    for msg in messages:
        if msg is not None:
            yield msg