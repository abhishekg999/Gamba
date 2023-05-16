from datetime import datetime
import finnhub
import websocket
import rel
import time
import json
import threading

print_lock = threading.Lock()

with open("api.key", "r") as f:
    API_KEY = f.read()

def unix_to_date(t):
    return datetime.fromtimestamp(t)

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


def on_message(ws, message):
    data = json.loads(message)
    with print_lock:
        print(data)
    
def on_error(ws, error):
    with print_lock:
        print(error)


def on_close(ws, close_status_code, close_msg):
    with print_lock:
        print("### closed ###")
    


def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"AAPL"}')
    ws.send('{"type":"subscribe","symbol":"AMZN"}')
    ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')


def runner():
    for i in range(100):
        with print_lock:
            print(i)
        
        time.sleep(1)

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
    threads = main(runner)

    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(
        f"wss://ws.finnhub.io?token={API_KEY}",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )

    ws.run_forever(skip_utf8_validation=True)

    for thread in threads:
        thread.join()


