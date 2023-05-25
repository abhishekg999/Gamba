import json
import os
import threading
import time
from datetime import datetime

import websocket
from dotenv import load_dotenv

from context import ThreadContextManager
from redis_server import R
from stock_client import CLIENT

load_dotenv()
API_KEY = os.getenv("FINNHUB_API_KEY")

R_pipeline = R.pipeline()
R_sub = R.pubsub()

def handle_live_trades():
    """
    Handles life trade data. 

    Use live data directly and discard for limit buys and sells.
    """
    lifespan = 5

    def on_message(ws, message: bytes):
        data = json.loads(message.decode())
        print(data)

    def on_error(ws, error):
        print(error)

    def on_close(ws, close_status_code, close_msg):
        print("Websocket closed.")

    def on_open(ws):
        ws.send('{"type":"subscribe","symbol":"AAPL"}')
        ws.send('{"type":"subscribe","symbol":"AMZN"}')
        ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')

        # initialize exit handler to exit websocket
        if lifespan:
            exit_handler = threading.Timer(lifespan, ws.close)
            exit_handler.start()

    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(
        f"wss://ws.finnhub.io?token={API_KEY}",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )

    ws.run_forever(skip_utf8_validation=True)


def handle_option_chain_cache():
    """
    Stores SPY option chain data to redis server
    """
    while True:
        # handle exit condition
        if R.get("handler:global_exit") == "quit":
            return

        remote = CLIENT.fetch_option_chain("SPY")
        res = json.loads(remote)

        code = res.get("code", None)

        # probably not the cleanest
        if not code:
            time.sleep(5)
            print("in handle_option_chain: error in fetching data")
            continue

        expirations = res.get("data", [])
        for expiry in expirations:
            options = expiry["options"]

            calls = options.get("CALL", [])
            for call in calls:
                contract_name = call["contractName"]
                last_price = call["lastPrice"]
                key = f"option_chain:{code}:{contract_name}:lastPrice"
                R_pipeline.set(key, last_price)

            puts = options.get("PUT", [])
            for put in puts:
                contract_name = put["contractName"]
                last_price = put["lastPrice"]
                key = f"option_chain:{code}:{contract_name}:lastPrice"
                R_pipeline.set(key, last_price)

        R_pipeline.execute()
        time.sleep(5)


if __name__ == "__main__":
    with ThreadContextManager(handle_live_trades) as threads:
        res = CLIENT.fetch_quote("BINANCE:BTCUSDT")
        print("Last price: " + str(res["c"]))
        assert res["t"] != 0
