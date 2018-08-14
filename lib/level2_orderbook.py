# TODO: use cdecimal to speed up
from   decimal import Decimal

from   enum import Enum
from   sortedcontainers import SortedDict


class Side(Enum):
    BID = 1
    ASK = -1


class Level2Orderbook:
    def __init__(self):
        self._asks = SortedDict()
        self._bids = SortedDict()


    @staticmethod
    def _update_side(levels, price, size):
        if size == 0:
            del levels[Decimal(price)]
        else:
            levels[Decimal(price)] = size


    @staticmethod
    def _get_size(levels, price):
        return levels.get(Decimal(price), 0)


    def update_level(self, side, price, size):
        levels = self._asks if side == Side.ASK else self._bids
        Level2Orderbook._update_side(levels, price, size)


    def update_ask(self, price, size):
        Level2Orderbook._update_side(self._asks, price, size)


    def update_bid(self, price, size):
        Level2Orderbook._update_side(self._asks, price, size)


    def get_level(self, side, price):
        levels = self._asks if side == Side.ASK else self._bids
        return Level2Orderbook._get_size(levels, price)


    def get_ask(self, price):
        return Level2Orderbook._get_size(self._asks, price)


    def get_bid(self, price):
        return Level2Orderbook._get_ask(self._bids, price)


    # TODO: what to do if no asks?
    def best_ask(self):
        return self._asks.items()[0]


    def best_bid(self):
        return self._bids.items()[0]


    # TODO: pad with NaN if depth not enough??
    def best_asks(self, max_depth):
        return self._asks.items()[:max_depth]


    def best_bids(self, max_depth):
        return self._bids.items()[:max_depth]
