from datetime import datetime, timezone
import pytz
import dill as pickle
import os
from pathlib import Path
import shutil




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
    
    dir_path = 'jar/'
    total_path = dir_path + at
    
    return total_path


import os
import shutil
import asyncio

async def move_pickle(id, to, fro):
   # Step 1: Look for the file in the 'from' directory
   from_path = f'jar/{fro}'
   filename = f'{id}.pkl'  
   source_file = os.path.join(from_path, filename)
   
   # Check if file exists
   if not os.path.exists(source_file):
       print(f"File {filename} not found in {from_path}")
   
   # Step 2: Handle based on fro value
   if fro == 3:
       # Delete the file if fro is 3
       try:
           os.remove(source_file)
           print(f"Deleted {filename} from {from_path}")
       except Exception as e:
           print(f"Error deleting {filename}: {e}")
   else:
       # Move file to 'to' directory
       to_path = f'jar/{to}'
       
       # Create destination directory if it doesn't exist
       os.makedirs(to_path, exist_ok=True)
       
       destination_file = os.path.join(to_path, filename)
       
       try:
           shutil.move(source_file, destination_file)
           print(f"Moved {filename} from {from_path} to {to_path}")
       except Exception as e:
           print(f"Error moving {filename}: {e}")

# Usage example:
# await move_pickle(123, 1, 2)  # Move 123.pickle from jar/2 to jar/1
# await move_pickle(456, 1, 3)  # Delete 456.pickle from jar/3

async def save_pickle(items, at):
    total_path = pickle_processing(at)
    with open(total_path, 'wb') as f:
        pickle.dump(items, f)

    #god i hope this works


#not in use till i move beyond lazy loading
def load_pickle(at):
    total_path = pickle_processing(at)
    with open(total_path, 'rb') as f:
        return pickle.load(f)
    
def load_whole_pickles_jar(at = 'jar', *target) -> list[list]:
    """
        LIST OF LIST OF OBJECTS
        INDEX CORRESPONDS WITH COLUMN
        DONT BE STUPID
    """
    all_pickles = []
    if not target:
        target = range(3) #then all of them
    for i in target:
        if i > 2 or i < 0: continue #i dont care about the invalid
        path = at + '/' + str(i)
        os.makedirs(path, exist_ok=True)
        all_pickles.append(load_pickles_from(path))
    return all_pickles

def load_pickles_from(at):
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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("process_name", type=str, help="Name of the process") # i thought the 
    parser.add_argument('user_id', type=int, 
                    help='pkl id')
    parser.add_argument('to', type = int)
    args = parser.parse_args()
    if args.process_name == 'move_update':
        asyncio.run(move_pickle(args.user_id, args.to, args.to - 1))


