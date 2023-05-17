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
from redis_server import R

from context import ThreadContextManager

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")
PARSE_OPTION_STRING_RE = r"^([A-Z]*)(\d{2})(\d{2})(\d{2})([CP])(\d*)$"

R_pipeline = R.pipeline()
print_lock = threading.Lock()


def unix_to_date(t):
    return datetime.fromtimestamp(t)


def parse_option_symbol(contract: str):
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


class StockClient:
    def __init__(self) -> None:
        self._api_key = API_KEY
        self.finnhub_client = finnhub.Client(api_key=self._api_key)

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


client = StockClient()


def handle_option_chain_cache():
    """
    Stores SPY option chain data to redis server
    """
    while True:
        remote = client.fetch_option_chain("SPY")
        res = json.loads(remote)
        
        code = res.get("code", None)

        # remove this
        if not code:
            time.sleep(5)
            break

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


def main(*runners):
    threads = []
    for runner in runners:
        t = threading.Thread(target=runner)
        t.daemon = True
        threads.append(t)

    for thread in threads:
        thread.start()

    return threads


if __name__ == "__main__":
    # initialize all other threads
    # threads = main()

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

    with ThreadContextManager(handle_option_chain_cache) as threads:
        print(parse_option_symbol("SPY230516C00330000"))
