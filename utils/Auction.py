import heapq

class Auction():
    def __init__(self, root : int, items : list):
        self.images = items
        self._root = root


    def get_root(self) -> int:
        return self._root


        #as a side note i wanted to use self.bids = heapq.heapify([]). but i thought about how much time that would take and decided against it
