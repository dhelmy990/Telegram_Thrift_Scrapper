from abc import abstractmethod, ABC
import re
from client import client


class Post(ABC):
    def __init__(self):
        self.best_buyer = None
        self.offer = 0
        self.predicted_price = -float('inf') #dummy value for now. All must go!

    def get_all_images(self):
        give = []
        #print(len(self.items))
        for each in self.items:
            give.append(each.media)
        return give

    async def _set_buy_n_price_(self, b, o):
        self.best_buyer = b
        self.offer = o

    async def get_best_buyer(self):
        if not self.offer_ready():
            raise KeyError
        user = await client.get_entity(self.best_buyer)
        val = user.username
        return val if val is not None else "[BUYER DID NOT SET]"


    
    
    
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
    def get_text() -> str:
        pass

    @abstractmethod
    def get_original_price(self) -> int:
        pass

    @staticmethod
    def Factory(msg: int, cluster: list): #TODO typecast the msg as wtv the object for msg is
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
                    msg=msg
                )
            elif 'fcfs' in text:    
                return FCFS(
                    root=msg.id, 
                    items=cluster, 
                    sb=cost, 
                    msg=msg
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

    
class FCFS(Post):
    def __init__(self, root : int, items : list, sb, msg):
        super().__init__()
        self.items = items
        self._root = root
        self.sb = sb
        self.msg = msg

        #TODO figure out SB
        #TODO figure out FCFS oh you know what i realise its not 
        #TODO have SB and FCFS inherit from Post at the same time

    def get_text(self) -> str:
        return self.msg.text if self.msg.text is not None else ""

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
    def __init__(self, root : int, items : list, sb, msg=None):
        super().__init__()
        self.items = items
        self._root = root
        self.sb = sb
        self.msg = msg

    def get_text(self) -> str:
        return self.msg.text if self.msg.text is not None else ""

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
            if offer > best_bid:
                best_bid = offer
                best_bidder = reply.sender_id

        await self._set_buy_n_price_(best_bidder, best_bid)
