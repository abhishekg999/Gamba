import finnhub
import multiprocessing
import uuid
from datetime import datetime
import websocket
import rel
import json

with open("api.key", "r") as f:
    API_KEY = f.read()

finnhub_client = finnhub.Client(api_key=API_KEY)

def fetch_quote(symbol, queue=None):
    """
    Gets stock quote for a ticker.

    Args:
        symbol (str): Stock ticker
    """
    res = finnhub_client.quote(symbol=symbol)

    if queue:
        queue.put((symbol, res))

    return res

def fetch_option_chain(symbol, queue=None):
    """
    Gets option chain for a ticker.

    Args:
        symbol (str): Stock ticker
    """
    res = finnhub_client.option_chain(symbol=symbol)

    if queue:
        queue.put((symbol, res))

    return res


def unix_to_date(t):
    return datetime.fromtimestamp(t)


def on_message(ws, message):
    data = json.loads(message)
    print(data)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"AAPL"}')
    ws.send('{"type":"subscribe","symbol":"AMZN"}')
    ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')

if __name__ == "__main__":
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={API_KEY}",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              on_open = on_open)

    ws.run_forever(dispatcher=rel, reconnect=5, skip_utf8_validation=True)
    rel.signal(2, rel.abort)
    rel.dispatch()
