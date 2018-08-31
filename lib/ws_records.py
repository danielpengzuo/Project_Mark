import ast
import dateutil.parser
from   decimal import Decimal
import json
import logging
import pandas as pd

from   .level2_orderbook import Level2Orderbook
from   .mktdata_serializer import DictCsvSerializer


# TODO: parse_capture?
def parse_record(line):
    line = ast.literal_eval(line)
    return {
        "receive_time": dateutil.parser.parse(line["receive_time"]),
        "message"     : json.loads(line["raw"])
    }


class HitbtcTradeCaptureToCsv:
    """
    Encapsulates conversion logic + an environment for conversion stats.
    """
    FIELDS = ('recv_time', 'timestamp', 'id', 'price', 'quantity', 'side')
    SERIALIZER = DictCsvSerializer(FIELDS)


    def __init__(self):
        self._snapshot_cnt = 0
        self._multiple_trade_cnt = 0
        self._ack_cnt = 0


    def header(self):
        return self.SERIALIZER.header()


    def capture_to_csv_rows(self, capture):
        message = capture["message"]
        if "method" not in message:
            self._ack_cnt += 1
            return
        if message["method"] != "updateTrades":
            assert message["method"] == "snapshotTrades"
            self._snapshot_cnt += 1
            return
        data = message["params"]["data"]
        if len(data) > 1:
            self._multiple_trade_cnt += 1
            return
        recv_time = capture["receive_time"].isoformat()
        for trade in data:
            trade["recv_time"] = recv_time
            yield self.SERIALIZER.dict_to_row(trade)


    def conversion_stats(self):
        return '\n'.join((
            f"Ack: {ack_cnt}",
            f"other methods: {snapshot_cnt}",
            f"more than one trade: {multiple_trade_cnt}"
        ))


def trade_capture_files_to_csv_hitbtc(capture_files, csv_output):
    if isinstance(capture_files, str):
        capture_files = [ capture_files ]

    conv = HitbtcTradeCaptureToCsv()

    # helper
    def get_csv_lines():
        yield conv.header()
        for capture_file in capture_files:
            for line in open(capture_file, 'r'):
                capture = parse_record(line)
                yield from conv.capture_to_csv_rows(capture)

    # TODO: add gzip
    with open(csv_output, 'w') as output:
        for line in get_csv_lines():
            print(line, file=output)


def _market_snapshot_cols(depth):
    """
    Generate columns for order book levels like

    bid_2, bid_size_2, bid_1, bid_size_1, ask_1, ask_size_1, ask_2, ask_size_2
    """
    cols = []

    def add_level(side, index):
        cols.append(f"{side}_{index}")
        cols.append(f"{side}_size_{index}")

    for i in range(depth):
        add_level('bid', depth - i)

    for i in range(depth):
        add_level('ask', i + 1)

    return cols


# TODO: this is too special; separate into
# load + book_building + output limited depth
def load_hitbtc_orderbook(filenames, output_depth=3):
    """
    Load orderbook raw data and convert to pd.DataFrame.
    """
    if isinstance(filenames, str):
        filenames = [ filenames ]

    book = Level2Orderbook()
    snapshot_cnt = 0
    non_method_cnt = 0
    last_output = None

    record_collector = []

    def load_single_file(filename):
        nonlocal last_output
        nonlocal non_method_cnt
        nonlocal snapshot_cnt
        with open(filename, 'r') as input_file:
            for line in input_file:
                struct = parse_record(line)
                message = struct["message"]
                if 'method' not in message:
                    non_method_cnt += 1
                    continue
                if message['method'] == 'snapshotOrderbook':
                    snapshot_cnt += 1
                    book.clear()
                # Only apply updates to solid books.
                if snapshot_cnt == 0:
                    continue
                recv_time = struct["receive_time"]
                params = message['params']
                for ask in params['ask']:
                    book.update_ask(ask['price'], ask['size'])
                for bid in params['bid']:
                    book.update_bid(bid['price'], bid['size'])
                # TODO: check that we've seen snapshot message
                # TODO: handle not enough depth
                pairs = book.best_bids(output_depth) + book.best_asks(output_depth)
                if pairs != last_output:
                    last_output = pairs
                    seq = params['sequence']
                    row = [element for pair in ([(seq, recv_time)] + pairs) for element in pair ]
                    record_collector.append(row)

    for filename in filenames:
        load_single_file(filename)

    # TODO: log level...
    logging.warning(f"snapshot given {snapshot_cnt} times")
    logging.warning(f"{non_method_cnt} messages doesn't have 'method'")

    market_snapshot_cols = _market_snapshot_cols(output_depth)
    total_cols = ['sequence', 'recv_time'] + market_snapshot_cols

    df = pd.DataFrame(record_collector, columns=total_cols).set_index('sequence')
    for col in market_snapshot_cols:
        df[col] = pd.to_numeric(df[col])

    return df


