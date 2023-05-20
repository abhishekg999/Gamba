import json
import os
import threading
import time
from datetime import datetime

from context import ThreadContextManager
from redis_server import R
from stock_client import CLIENT


R_pipeline = R.pipeline()

def handle_incoming_live_trades(channel):
    """
    Handles incoming live trades from subscribed channels.

    User trades will be stored in a hashset type structure of the form:

    {
        "TICKER": []
    }

    List will be sorted in order of purchase made.
    Incoming trades will either try to fill in order of the queue.
    If any trade does not want partial execution, it will only try to be filled as a whole.

    Live trades are treated as liquidity for simulated trades in this artifical market.

    Args:
        channel (_type_): _description_
    """
    subscriber = R.pubsub()
    subscriber.subscribe(channel)

    for message in subscriber.listen():
        print(message)
        if (message['data'] == 'quit'):
            print(f"handler({channel}) stopping!!")
            break




if __name__ == "__main__":
    stocks = ['SPY', 'MSFT']
    threads = []

    for stock in stocks:
        t = threading.Thread(target=handle_incoming_live_trades, args = (f"channel:trades:{stock}",))
        t.daemon = True

        threads.append(t)


    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()