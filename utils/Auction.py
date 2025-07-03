from abc import abstractmethod, ABC
import re
import base64
import asyncio
import os
from client import client, get_username


class Post(ABC):
    def __init__(self):
        self.best_buyer = None
        self.offer = 0
        self.predicted_price = -float('inf') #dummy value for now. All must go!
        # Store both original media objects and their string representations
        self._media_objects = []  # Original Telegram media objects
        self._media_strings = []  # String representations for serialization

    def get_all_images(self):
        """Returns the original Telegram media objects for downloading"""
        return self._media_objects
    
    def get_media_strings(self):
        """Returns string representations of media for serialization"""
        return self._media_strings
    
    def set_media(self, media_objects):
        """Set both media objects and their string representations"""
        self._media_objects = media_objects
        self._media_strings = [str(obj) for obj in media_objects]
    
    async def fletify_image(self):
        """Download and save the first image for Flet display"""
        if not self._media_objects:
            return None
            
        path = 'media/'+ str(self.get_root())
        if not os.path.exists(path):
            # Ensure media directory exists
            os.makedirs('media', exist_ok=True)
            
            get = self._media_objects[0]  # Use original media object
            raw_bytes = await client.download_media(get, file=bytes)
            with open(path, 'wb') as f:
                f.write(raw_bytes) 
        return path
    
    def flet_image(self):
        """Return base64 encoded image for Flet display"""
        path = 'media/'+ str(self.get_root())
        if not os.path.exists(path):
            return None
        with open(path, 'rb') as r:
            raw_bytes = r.read()
        return base64.b64encode(raw_bytes).decode()

    async def _set_buy_n_price_(self, b, o):
        self.best_buyer = b
        self.offer = o
        self.best_buyer_name = await self.get_best_buyer()

    async def get_best_buyer(self):
        if not self.offer_ready():
            raise KeyError
        return await get_username(self.best_buyer)
        
    def offer_ready(self):
        #note for the time being, the second of these two terms returns True in all cases
        return (self.best_buyer is not None and self.offer > self.predicted_price)    
        
    @abstractmethod
    def get_root(self) -> int:
        pass

    @abstractmethod
    def gavel(self, channel_username, client) -> int:
        pass

    @abstractmethod
    def get_text(self) -> str:  # Fixed: added self parameter
        pass

    @abstractmethod
    def get_original_price(self) -> int:
        pass

    @staticmethod
    def Factory(msg, cluster: list):  # Fixed: removed incorrect type hint for msg
        """
        Factory method to create an Auction or FCFS object based on the message text.
        If the text contains 'sb', it creates an Auction object.
        If the text contains 'fcfs', it creates an FCFS object.
        If neither is found, it returns None.
        It also has the responsibility of extracting the cost of the FCFS or the  from the text.
        """
        texts = msg.text.lower().split('\n')
        print(len(cluster))
        for text in texts:
            cost = Post.extract_cost(text)
            if cost is None:
                continue
            elif 'sb' in text:
                return Auction(
                    root=msg.id, 
                    items=cluster, 
                    sb=cost,
                    text=text
                )
            elif 'fcfs' in text:    
                return FCFS(
                    root=msg.id, 
                    items=cluster, 
                    sb=cost, 
                    text = text
                )  
        return None
    
    @staticmethod
    def extract_cost(text, from_reply = False):
        """
            This is a custom method to return the cost of the item from a given line of text.
            But when specified as free, then it returns 0
        """
        if 'free' in text.lower():
            return 0
        number = re.search(r'\d+', text)
        if number is None:
            return None
        return int(number.group())

    def to_serializable_dict(self):
        """Create a serializable dictionary representation for UI/pickling"""
        return {
            'root': self.get_root(),
            'text': self.get_text(),
            'original_price': self.get_original_price(),
            'best_buyer': self.best_buyer,
            'offer': self.offer,
            'best_buyer_name': getattr(self, 'best_buyer_name', None),
            'media_strings': self._media_strings,
            'predicted_price': self.predicted_price,
            'class_type': self.__class__.__name__
        }

class FCFS(Post):
    def __init__(self, root : int, items : list, sb, text):
        super().__init__()
        # Extract media objects from items and store them properly
        media_objects = [item.media for item in items if hasattr(item, 'media') and item.media]
        self.set_media(media_objects)
        self._root = root
        self.sb = sb
        self.text = text

    def get_text(self) -> str:
        return self.text if self.text is not None else ""

    def get_root(self) -> int:
        return self._root
    
    def get_original_price(self) -> int:
        """
            Returns the original price of the item.
            This is the SB price for FCFS.
        """
        return self.sb    

    def extract_offer(self, text): #TODO make this a method taking only replies in
        """
           Extracts price from text. when they say "me" they're following the FCFS
        """
        if 'me' in text.lower():
            return self.sb
        number = re.search(r'\d+', text)
        if number is None:
            return None
        return int(number.group())

    async def gavel(self, channel_username, client):
        """        Determines who is the first to claim the item.
            Returns the sender ID of the first message that replies to the root post.
        """
        #print(self.get_root, self.get_text), forgot what this line was for
        
        async for reply in client.iter_messages(channel_username, reply_to=self.get_root()):
            cost = self.extract_offer(reply.text)
            await self._set_buy_n_price_(reply.sender_id, cost)
            return
        
            

class Auction(Post):
    def __init__(self, root : int, items : list, sb, text=None):
        super().__init__()
        # Extract media objects from items and store them properly
        media_objects = [item.media for item in items if hasattr(item, 'media') and item.media]
        self.set_media(media_objects)
        self._root = root
        self.sb = sb
        self.text = text

    def get_text(self) -> str:
        return self.text if self.text is not None else ""

    def get_root(self) -> int:
        return self._root
        
    def get_original_price(self) -> int:
        """
            Returns the original price of the item.
            This is the SB price for FCFS.
        """
        return self.sb
    
    def extract_offer(self, text): #TODO make this a method taking only replies in
        """
           Extracts price from text. when they say "me" they're following the FCFS
        """
        if 'sb' in text.lower():
            return self.sb
        number = re.search(r'\d+', text)
        if number is None:
            return None
        return int(number.group())
    
    async def gavel(self, channel_username, client):
        """
            Determines who is the highest bidder.
        """
        best_bid = 0
        best_bidder = None
        async for reply in client.iter_messages(channel_username, reply_to=self.get_root()):
            offer = self.extract_offer(reply.text)
            if offer is None:
                continue
            if offer >= self.sb and offer > best_bid:
                best_bid = offer
                best_bidder = reply.sender_id

        await self._set_buy_n_price_(best_bidder, best_bid)

    def load_best_buyer(self):
        try:
            return self.best_buyer_name
        except:
            return None