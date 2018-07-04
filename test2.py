import websocket
import json 

try:
    import thread
except ImportError:
    import _thread as thread
import time

def on_message(ws, message):
    res = eval(message)
    #print(type(res))
    #print(res['jsonrpc'])
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    #def run(*args):
    #subscribe to order book
    ws.send('{ "method": "subscribeOrderbook", "params": { "symbol": "TRXETH" }, "id": 123 }')
    #subscribe to trades
    ws.send('{ "method": "subscribeTrades", "params": { "symbol": "TRXETH" }, "id": 123 }')
    #thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://api.hitbtc.com/api/2/ws",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()