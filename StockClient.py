from datetime import datetime
import finnhub
import websocket
import rel
import time
import json
import threading
from dotenv import load_dotenv
import os
import re
from RedisServer import R

from context import ThreadContextManager

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")
PARSE_OPTION_STRING_RE = r"^([A-Z]*)(\d{2})(\d{2})(\d{2})([CP])(\d*)$"

R_pipeline = R.pipeline()
print_lock = threading.Lock()


def unix_to_date(t):
    return datetime.fromtimestamp(t)


def parse_option_symbol(contract: str) -> dict[str, int] | None:
    match = re.match(PARSE_OPTION_STRING_RE, contract)
    if match is None:
        return None

    groups = match.groups()
    keys = ["symbol", "year", "month", "day", "type", "strike"]

    try:
        assert len(groups) == len(keys)
        ret = dict(zip(keys, groups))
        ret["year"] = int(ret["year"])
        ret["month"] = int(ret["month"])
        ret["day"] = int(ret["day"])
        ret["strike"] = float(ret["strike"][:-3] + "." + ret["strike"][-3:])
        return ret
    except (AssertionError, ValueError):
        return None


def option_to_contract_name(option_data: dict[str, int]):
    option_data["strike"] = int(option_data["strike"] * 1000)
    return f"{option_data['symbol']}{option_data['year']:02}{option_data['month']:02}{option_data['day']:02}{option_data['type']}{option_data['strike']:08}"


class StockClient:
    def __init__(self) -> None:
        self._api_key = API_KEY
        self.finnhub_client = finnhub.Client(api_key=self._api_key)

        # manually increase Client timeout since option chain request might take a sec
        self.finnhub_client.DEFAULT_TIMEOUT = 30  # type: ignore

        # fetch periodically
        self.supported_symbols = ["AAPL", "MSFT", "GOOGL", "SPY"]

    def is_supported_symbol(self, symbol):
        return symbol in self.supported_symbols

    def fetch_quote(self, symbol, queue=None):
        """
        Gets stock quote for a ticker.

        Args:
            symbol (str): Stock ticker
        """
        res = self.finnhub_client.quote(symbol=symbol)

        if queue:
            queue.put((symbol, res))

        return res

    def fetch_option_chain(self, symbol, queue=None):
        """
        Gets option chain for a ticker.

        Args:
            symbol (str): Stock ticker
        """
        res = self.finnhub_client.option_chain(symbol=symbol)

        if queue:
            queue.put((symbol, res))

        return res


CLIENT = StockClient()


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
    # initialize all other threads

    # websocket.enableTrace(False)
    # ws = websocket.WebSocketApp(
    #     f"wss://ws.finnhub.io?token={API_KEY}",
    #     on_message=on_message,
    #     on_error=on_error,
    #     on_close=on_close,
    #     on_open=on_open,
    # )

    # ws.run_forever(skip_utf8_validation=True)

    # for thread in threads:
    #     thread.join()

    # with ThreadContextManager(handle_option_chain_cache) as threads:
    #     option = "SPY230516C00330000"
    #     parsed = parse_option_symbol(option)

    #     assert parsed is not None
    #     back = option_to_contract_name(parsed)
    #     assert option == back

    with ThreadContextManager(handle_live_trades) as threads:
        res = CLIENT.fetch_quote("BINANCE:BTCUSDT")
        print("Last price: " + str(res["c"]))
        assert res["t"] != 0
