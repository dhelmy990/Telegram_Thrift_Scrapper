from abc import abstractmethod, ABC
import re

class Post(ABC):
    @abstractmethod
    def get_root(self) -> int:
        pass

    @abstractmethod
    def gavel(self, channel_username, client) -> int:
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
        for text in texts:
            cost = Post.extract_cost(text)
            if cost is None:
                continue
            elif 'sb' in text:
                return Auction(
                    root=msg.id, 
                    items=cluster, 
                    sb=cost
                )
            elif 'fcfs' in text:    
                return FCFS(
                    root=msg.id, 
                    items=cluster, 
                    sb=cost
                )  
        return None
    
    @staticmethod
    def extract_cost(text):
        """
            This is a custom method to return the cost of the item from a given line of text.
            But if it's specified as free, then it returns 0
        """
        if 'free' in text.lower():
            return 0
        number = re.search(r'\d+', text)
        if number is None:
            return None
        return int(number.group())
    
class FCFS(Post):
    def __init__(self, root : int, items : list, sb):
        self.images = items
        self._root = root
        self.sb = sb
        #TODO figure out SB
        #TODO figure out FCFS oh you know what i realise its not 
        #TODO have SB and FCFS inherit from Post at the same time


    def get_root(self) -> int:
        return self._root
        
    async def gavel(self, channel_username, client):
        """        Determines who is the first to claim the item.
            Returns the sender ID of the first message that replies to the root post.
        """
        async for reply in client.iter_messages(channel_username, reply_to=self.get_root()):
            cost = Post.extract_cost(reply.text)
            if reply.sender_id is not None and cost is not None:
                return reply.sender_id, cost


class Auction(Post):
    def __init__(self, root : int, items : list, sb):
        self.images = items
        self._root = root
        self.sb = sb


    def get_root(self) -> int:
        return self._root
        
    async def gavel(self, channel_username, client):
        """
            Determines who is the highest bidder.
        """
        best_bid = 0
        best_bidder = None
        async for reply in client.iter_messages(channel_username, reply_to=self.get_root()):
            offer = Post.extract_cost(reply.text)
            if offer is None:
                continue
            if offer > best_bid:
                best_bid = offer
                best_bidder = reply.sender_id

        return best_bidder, best_bid
