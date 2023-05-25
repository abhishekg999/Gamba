from flask import request
from utils import jsonret
from jwts import get_username_from_token
from database import User, db, DB_LOCK
from stock_client import CLIENT
import decimal

# pylint: disable-next=E0611
from __main__ import app


def validate_symbol(symbol: str | None):
    if not symbol:
        return False

    if not CLIENT.is_supported_symbol(symbol):
        return False

    return True


def validate_amount(amount: str | None):
    if not amount:
        return False

    # allow only whole number shares for now
    if not amount.isdigit():
        return False

    return True


@app.route("/stocks/buy", methods=["GET"])
@jsonret
def buy():
    token = request.values.get("token")
    _symbol = request.values.get("symbol")
    _amount = request.values.get("amount")

    if not validate_symbol(_symbol):
        ret = {"error": "Invalid or unsupported stock symbol"}
        return ret

    assert _symbol is not None
    symbol = _symbol

    if not validate_amount(_amount):
        ret = {"error": "Invalid amount specified"}
        return ret

    assert _amount is not None
    amount = int(_amount)

    username = get_username_from_token(token)

    if not username:
        ret = {"error": "Token invalid or not provided"}
        return ret

    # make api call before entering lock
    last_quote = CLIENT.fetch_quote(symbol)
    last_price = last_quote["c"]

    total_user_cost = last_price * amount

    with DB_LOCK:
        user = User.query.filter_by(username=username).first()
        if not user:
            ret = {"error": "Token invalid or not provided"}
            return ret

        if user.money < total_user_cost:
            ret = {"error": "Not enough money to purchase"}
            return ret

        user.money -= decimal.Decimal(total_user_cost)

        assets = user.assets
        print(type(assets))
        if symbol in assets:
            user.assets[symbol] += amount
        else:
            user.assets[symbol] = amount

        db.session.commit()
        ret = {"stocks": "buy", "balance": user.money, "assets": user.assets, "message": f"Bought {amount} shares for {last_price} a share, {total_user_cost} in total spent"}

    return ret

# TODO: Need to add sell
# TODO: eventually completely remove these and implement limit_buy and limit_sell
# TODO: have a worker thread listen to the webserver and store quote data in redis server, then fetch from redis
# TODO: implement transition states for purchase when having limit buy / sell, use redis hmap with expiry?