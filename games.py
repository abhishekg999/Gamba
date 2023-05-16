from flask import request
import random
from utils import jsonret
from jwts import get_username_from_token
from account import User, db
import decimal

# pylint: disable-next=E0611
from __main__ import app, limiter

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

    if bet is None or target is None:
        ret = {"error": "Invalid arguments, require token, bet, target."}
        return ret

    try:
        bet_value = int(bet)
    except ValueError:
        ret = {"error": "Invalid bet provided"}
        return ret
    
    if bet_value < 1:
        ret = {"error": "Invalid bet provided"}
        return ret
    
    try:
        target_value = float(target)
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
    
    user = User.query.filter_by(username=username).first()
    if not user:
        ret = {"error": "Token invalid or not provided"}
        return ret
    
    if user.money < bet_value:
        ret = {"error": "Not enough money in account to bet that much"}
        return ret

    lower_value = random.randint(0, 100)
    multiplier = 100 / target_value

    if lower_value >= target_value:
        user.money -= bet_value
        result = 'lose'
        change = -bet_value
    else:
        user.money = user.money + decimal.Decimal(-bet_value + bet_value * multiplier)
        result = 'win'
        change = bet_value * multiplier

    db.session.commit()
    ret = {"game": "lower", "bet": bet_value, "target": target_value, "result": result, "value": lower_value, "change": bet_value, "balance": user.money }

    return ret

@app.route("/beg", methods=["GET"])
@limiter.limit("1/minute")
@jsonret
def beg():
    token = request.values.get("token")
    username = get_username_from_token(token)

    if not username:
        ret = {"error": "Token invalid or not provided"}
        return ret
    
    user = User.query.filter_by(username=username).first()
    if not user:
        ret = {"error": "Token invalid or not provided"}
        return ret

    value = random.randint(1, 40)
    user.money += value

    db.session.commit()

    ret = {"game": "beg", "result": "win", "change": value, "balance": user.money}
    return ret

