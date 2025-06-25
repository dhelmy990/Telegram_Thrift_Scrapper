from datetime import datetime
import pytz


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
    
    sgt_timezone = pytz.timezone('Asia/Singapore')

    return sgt_timezone.localize(last_seen)


