from datetime import datetime
import finnhub
from dotenv import load_dotenv
import os
import re
from redis_server import R

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")
PARSE_OPTION_STRING_RE = r"^([A-Z]*)(\d{2})(\d{2})(\d{2})([CP])(\d*)$"

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
