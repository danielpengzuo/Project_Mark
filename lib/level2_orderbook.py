from   decimal import Decimal

from   enum import Enum
from   sortedcontainers import SortedDict


NaN = float('nan')


# TODO: move to general func
# TODO: try itertool version https://stackoverflow.com/a/3438986
def pad_list(base, target_len, padding):
    return base + [padding] * (target_len - len(base))


def pad_list_front(base, target_len, padding):
    return [padding] * (target_len - len(base)) + base


class Side(Enum):
    BID = 1
    ASK = -1


class Level2Orderbook:
    def __init__(self):
        self.clear()


    def clear(self):
        self._asks = SortedDict()
        self._bids = SortedDict()


    @staticmethod
    def _update_side(levels, price, size):
        price = Decimal(price)
        size = Decimal(size)
        if size == 0:
            del levels[price]
        else:
            levels[price] = size


    @staticmethod
    def _get_size(levels, price):
        return levels.get(Decimal(price), 0)


    def update_level(self, side, price, size):
        levels = self._asks if side == Side.ASK else self._bids
        Level2Orderbook._update_side(levels, price, size)


    def update_ask(self, price, size):
        Level2Orderbook._update_side(self._asks, price, size)


    def update_bid(self, price, size):
        Level2Orderbook._update_side(self._bids, price, size)


    def get_level(self, side, price):
        levels = self._asks if side == Side.ASK else self._bids
        return Level2Orderbook._get_size(levels, price)


    def get_ask(self, price):
        return Level2Orderbook._get_size(self._asks, price)


    def get_bid(self, price):
        return Level2Orderbook._get_ask(self._bids, price)


    def best_ask(self):
        """
        :return:
          A pair (best_ask_price, best_ask_size).
          (NaN, NaN) if there is no ask at all.
        """
        try:
            return self._asks.items()[0]
        except IndexError:
            return (NaN, NaN)


    def best_bid(self):
        """
        :return:
          A pair (best_bid_price, best_bid_size).
          (NaN, NaN) if there is no bid at all.
        """
        try:
            return self._bids.items()[0]
        except IndexError:
            return (NaN, NaN)


    # TODO: doc padding
    def best_asks(self, max_depth, padding=True):
        asks = self._asks.items()[:max_depth]
        if padding:
            return pad_list(asks, max_depth, (NaN, 0))
        else:
            return asks


    # TODO: reverse??
    def best_bids(self, max_depth, padding=True):
        bids = self._bids.items()[-max_depth:]
        if padding:
            return pad_list_front(bids, max_depth, (NaN, 0))
        else:
            return bids


    @property
    def depths(self):
        return len(self._bids), len(self._asks)
