import sqlite3
from typing import Optional, List, Tuple



def init_undone_bid(db_path: str = "db/undone_bid.db") -> None:
    """
    Initialize SQLite database with messages table.
    
    Args:
        db_path: Path to the database file
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table with teleid and rootid
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS undone_bid (
            teleid INTEGER NOT NULL,
            rootid INTEGER NOT NULL
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_rootid ON undone_bid(rootid)
    ''')
    

    
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")

def add_message(teleid: int, rootid: int, db_path: str = "db/undone_bid.db") -> int:
    """
    Add a message to the database.
    
    Args:
        teleid: Telegram message ID
        rootid: Root ID to group messages
        db_path: Path to the database file
        
    Returns:
        The row ID of the inserted record
    """
    #TODO simple add_message function. can it be used later on?

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO messages (teleid, rootid)
        VALUES (?, ?)
    ''', (teleid, rootid))
    
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return row_id

def add_message_collection(teleids: List[int], rootid, db_path: str = "db/undone_bid.db") -> int:
    """
    Add multiple messages with the same rootid.
    
    Args:
        teleids: List of telegram message IDs
        db_path: Path to the database file
        
    Returns:
        The rootid used for all messages
    """
    
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Insert all messages with the same rootid
    cursor.executemany('''
        INSERT INTO messages (teleid, rootid)
        VALUES (?, ?)
    ''', [(teleid, rootid) for teleid in teleids])
    
    conn.commit()
    conn.close()
    
    return rootid

def get_messages_by_root(rootid: int, db_path: str = "db/undone_bid.db") -> List[int]:
    #TODO adapt this to implementation of classes. All we need is to pass these to Post.Factory, one list at a time
    #TODO we also need to...um...i need a list of the unique ids. And for each of them I will need all of the messages pertaining to each id. That logic is handled upstaris
    """
    Get all telegram message IDs for a specific root.
    
    Args:
        rootid: Root ID to search for
        db_path: Path to the database file
        
    Returns:
        List of telegram message IDs
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT teleid FROM messages 
        WHERE rootid = ?
        ORDER BY id
    ''', (rootid,))
    
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return results

def get_all_unique_rootids(db_path: str = "db/undone_bid.db") -> List[int]:
    """
    Get all unique rootids from the database.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        List of unique rootids
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT rootid FROM undone_bid
        ORDER BY rootid
    ''')
    
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return results

    