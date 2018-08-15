import ast
import dateutil.parser
# TODO: use cdecimal
from   decimal import Decimal
import json
import logging
import pandas as pd


def parse_record(line):
    line = ast.literal_eval(line)
    return {
        "receive_time": dateutil.parser.parse(line["receive_time"]),
        "message"     : json.loads(line["raw"])
    }


def load_hitbtc_trades(filename):
    """
    (Just the new trades, not snapshots yet)
    """
    snapshot_cnt = 0
    multiple_trade_cnt = 0
    ack_cnt = 0
    trades = []
    for line in open(filename):
        struct = parse_record(line)
        message = struct["message"]
        if "method" not in message:
            ack_cnt += 1
            continue
        if message["method"] != "updateTrades":
            assert message["method"] == "snapshotTrades"
            snapshot_cnt += 1
            continue
        data = message["params"]["data"]
        if len(data) > 1:
            multiple_trade_cnt += 1
            continue
        for trade in data:
            trade["recv_time"] = struct["receive_time"]
            trades.append(trade)
            
        logging.info(f"Ack: {ack_cnt}")
        logging.info(f"other methods: {snapshot_cnt}")
        logging.info(f"more than one trade: {multiple_trade_cnt}")

    trades = pd.DataFrame.from_records(trades)
    return trades.astype(
        {'price': float,
         'quantity': float,
         'recv_time': "datetime64[us]",
         "timestamp" : "datetime64[us]" 
        }, copy=False
    )
