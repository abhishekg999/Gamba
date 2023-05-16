from flask import request
import random
from utils import jsonret
from jwts import get_username_from_token
from account import User, db

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
    value = random.randint(0, 100)
    ret = {"game": "lower", "value": value}

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

    ret = {"game": "beg", "change": value, "balance": user.money}
    return ret

