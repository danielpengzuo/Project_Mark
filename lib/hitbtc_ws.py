import argparse
from   datetime import datetime
import logging
import json

from  .basewebsocket import BaseWebSocket
from  .rotation_logger import rotation_logger


MEGA = 2 ** 20


class HitBtcWebSocket(BaseWebSocket):
    PUBLIC_WS = "wss://api.hitbtc.com/api/2/ws"

    # TODO: random id
    def __init__(self, symbol, feed, id=1):
        super().__init__(
            self.PUBLIC_WS, thread_name=f"hitbtc_ws-{symbol}"
        )
        self._symbol = symbol
        self._id = id
        self._feed = feed


    def __subscribe(self, method):
        self.ws.send(json.dumps({
            "method": method,
            "params": { "symbol": self._symbol },
            "id": self._id
        }))


    def on_connection(self):
        super().on_connection()
        self.__subscribe(f"subscribe{self._feed.capitalize()}")


class HitBtcWSLogger(HitBtcWebSocket):
    def __init__(self, symbol, feed, filepath, id=1):
        super().__init__(symbol, feed, id=id)
        self._filepath = filepath
        # TODO: tweak params
        self._logger = rotation_logger(
            filepath,
            maxBytes=100 * MEGA,
            backupCount=100
        )


    def on_message(self, msg):
        record = {
            "receive_time" : datetime.utcnow().isoformat(),
            "raw" : msg
        }
        self._logger.info(record)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', required=True)
    parser.add_argument('--log_path', required=True)
    parser.add_argument('--feed', required=True, help="orderbook, trade, etc.")
    args = parser.parse_args()

    logging.basicConfig(
        level='INFO',
        format='%(asctime)s - %(threadName)s [%(levelname)s] %(message)s'
    )

    hitbtc_logger = HitBtcWSLogger(
        args.symbol, args.feed, args.log_path
    )
    hitbtc_logger.start()
