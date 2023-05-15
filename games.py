from flask import jsonify
import random

# pylint: disable-next=E0611
from __main__ import app

@app.route("/coinflip", methods=["GET"])
def coinflip():
    ret = {"game": "coinflip", "value": random.choice(["heads", "tails"])}

    return jsonify(ret)

@app.route("/lower", methods=["GET"])
def lower():
    value = random.randint(0, 100)
    ret = {"game": "lower", "value": value}

    return jsonify(ret)
    
