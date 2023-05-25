from flask import request, g
import random
from utils import jsonret
from jwts import get_username_from_token
from database import User
import decimal

# pylint: disable-next=E0611
from __main__ import app


@app.route("/coinflip", methods=["GET"])
@jsonret
def coinflip():
    ret = {"game": "coinflip", "value": random.choice(["heads", "tails"])}

    return ret


@app.route("/lower", methods=["GET"])
@jsonret
def lower():
    token = request.values.get("token")
    bet = request.values.get("bet")
    target = request.values.get("target")

    if token is None or bet is None or target is None:
        ret = {"error": "Invalid arguments, require token, bet, target."}
        return ret

    try:
        bet_value = float(bet)
    except ValueError:
        ret = {"error": "Invalid bet provided"}
        return ret

    if bet_value < 0:
        ret = {"error": "Invalid bet provided"}
        return ret

    try:
        target_value = int(target)
    except ValueError:
        ret = {"error": "Invalid target provided"}
        return ret

    if target_value <= 0 or target_value > 100:
        ret = {"error": "Invalid target provided"}
        return ret

    username = get_username_from_token(token)

    if not username:
        ret = {"error": "Token invalid or not provided"}
        return ret

    try:
        g.session.begin_nested()
        user = g.session.query(User).filter_by(username=username).first()
        if not user:
            ret = {"error": "Token invalid or not provided"}
            return ret

        if user.money < bet_value:
            ret = {"error": "Not enough money in account to bet that much"}
            return ret

        lower_value = random.randint(0, 100)
        multiplier = 100 / target_value

        if lower_value >= target_value:
            result = "lose"
            change = -bet_value
        else:
            result = "win"
            change = -bet_value + bet_value * multiplier

        user.money += decimal.Decimal(change)
        g.session.commit()

        ret = {
            "game": "lower",
            "bet": bet_value,
            "target": target_value,
            "result": result,
            "value": lower_value,
            "change": change,
            "balance": user.money,
        }

    except Exception as err:
        g.session.rollback()
        ret = {"error": "unexpected error occured.", "traceback": str(err)}

    return ret


@app.route("/beg", methods=["GET"])
@jsonret
def beg():
    token = request.values.get("token")
    username = get_username_from_token(token)

    if not username:
        ret = {"error": "Token invalid or not provided"}
        return ret

    try:
        g.session.begin_nested()
        user = g.session.query(User).filter_by(username=username).first()
        if not user:
            ret = {"error": "Token invalid or not provided"}
            return ret

        value = 100

        user.money += value
        g.session.commit()

        ret = {"game": "beg", "result": "win", "change": value, "balance": user.money}

    except Exception as err:
        g.session.rollback()
        ret = {"error": "unexpected error occured.", "traceback": str(err)}
    return ret
