from datetime import datetime, timezone
import pytz
import dill as pickle
import os
from pathlib import Path



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


def pickle_processing(at):
    if isinstance(at, int):
        at = str(at)
    if 'pkl' not in at[-4:]:
        at = at + '.pkl'
    
    dir_path = 'pass_between/'
    total_path = dir_path + at
    
    return total_path


async def save_pickle(items, at):
    total_path = pickle_processing(at)
    with open(total_path, 'wb') as f:
        pickle.dump(items, f)

    #god i hope this works
    
def load_pickle(at):
    total_path = pickle_processing(at)
    with open(total_path, 'rb') as f:
        return pickle.load(f)

def load_pickles(at = 'pass_between'):
    pkl_names = list(Path(at).glob("*.pkl"))
    jar = []
    for pkl in pkl_names:
        with open(pkl, 'rb') as f:
            jar.append(pickle.load(f))
    return jar




def debug_pickle(obj):
    try:
        pickle.dumps(obj)
        print("Object can be pickled")
    except Exception as e:
        print(f"Pickle error: {e}")
        print(f"Object type: {type(obj)}")
        print(f"Object attributes: {dir(obj)}")
