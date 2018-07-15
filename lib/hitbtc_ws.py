import argparse
import logging
import json

from  .basewebsocket import BaseWebSocket
from  .rotation_logger import rotation_logger


MEGA = 2 ** 20


class HitBtcWebSocket(BaseWebSocket):
    PUBLIC_WS = "wss://api.hitbtc.com/api/2/ws"

    def __init__(self, symbol, id=1):
        super().__init__(
            self.PUBLIC_WS, thread_name=f"hitbtc_ws-{symbol}"
        )
        self._symbol = symbol
        self._id = id


    def __subscribe(self, method):
        self.ws.send(json.dumps({
            "method": method,
            "params": { "symbol": self._symbol },
            "id": self._id
        }))


    def on_connection(self):
        super().on_connection()
        self.__subscribe("subscribeOrderbook")
        self.__subscribe("subscribeTrades")


class HitBtcWSLogger(HitBtcWebSocket):
    def __init__(self, symbol, filepath, id=1):
        super().__init__(symbol, id=id)
        self._filepath = filepath
        # TODO: tweak params
        self._logger = rotation_logger(
            filepath,
            maxBytes=100 * MEGA,
            backupCount=100
        )


    def on_message(self, msg):
        self._logger.info(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', required=True)
    parser.add_argument('--log_path', required=True)
    args = parser.parse_args()

    logging.basicConfig(
        level='INFO',
        format='%(asctime)s - %(threadName)s [%(levelname)s] %(message)s'
    )

    hitbtc_logger = HitBtcWSLogger(args.symbol, args.log_path)
    hitbtc_logger.start()
