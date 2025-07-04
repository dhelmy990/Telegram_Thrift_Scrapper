import sqlite3


import sqlite3
import os

import sqlite3
import os

class AddressInfo:
    addresses_cache = {}
    DB_PATH = 'db/addresses.db'
    
    @staticmethod
    def _get_connection():
        """Get a database connection and ensure the table exists."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(AddressInfo.DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(AddressInfo.DB_PATH)
        conn.execute('CREATE TABLE IF NOT EXISTS addresses (id INTEGER PRIMARY KEY, address TEXT)')
        conn.commit()
        return conn
    
    @staticmethod
    def add_address(id, address: dict):
        """Add address to cache with validation."""
        try:
            required_keys = ['name', 'phone', 'address']
            for key in required_keys:
                if key not in address:
                    raise ValueError(f"Missing required key: {key}")
            
            AddressInfo.addresses_cache[id] = """
                Name: {name}
                Phone: {phone}
                Address: {address}
            """.format(
                name=address["name"], 
                phone=address["phone"], 
                address=address["address"]
            )
        except KeyError as e:
            raise ValueError(f"Invalid address data: missing {e}")
        
    @staticmethod
    def save_addresses():
        """Save all cached addresses to database."""
        with AddressInfo._get_connection() as conn:
            for id, address in AddressInfo.addresses_cache.items():
                # Use INSERT OR REPLACE to handle existing IDs
                conn.execute(
                    'INSERT OR REPLACE INTO addresses (id, address) VALUES (?, ?)', 
                    (id, address)
                )
            conn.commit()
    
    @staticmethod
    def load_addresses():
        """Load all addresses from database into cache."""
        with AddressInfo._get_connection() as conn:
            cursor = conn.execute('SELECT id, address FROM addresses')
            for id, address in cursor.fetchall():
                AddressInfo.addresses_cache[id] = address
        
    @staticmethod
    def del_address(id):
        """Delete address from both cache and database."""
        # Remove from cache if exists
        if id in AddressInfo.addresses_cache:
            del AddressInfo.addresses_cache[id]
        
        # Remove from database
        with AddressInfo._get_connection() as conn:
            conn.execute('DELETE FROM addresses WHERE id = ?', (id,))
            conn.commit()

    @staticmethod
    def get_address(id):
        """Get address from cache."""
        return AddressInfo.addresses_cache.get(id)

# Example usage:
if __name__ == "__main__":
    # Load existing addresses
    AddressInfo.load_addresses()
    
    # Add new address
    address_data = {
        "name": "John Doe",
        "phone": "555-0123",
        "address": "123 Main St, City, State"
    }
    AddressInfo.add_address(-1, address_data)
    
    # Save to database
    AddressInfo.save_addresses()
    
    # Get address
    print(AddressInfo.get_address(-1))

