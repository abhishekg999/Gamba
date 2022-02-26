from flask import Flask
app = Flask(__name__)


from flask import request, jsonify, flash
from flask import abort, redirect, url_for

from markupsafe import escape
import json

import random
import sqlite3
from sqlite3 import Error

import account


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


@app.route('/coinflip', methods=['GET'])
def coinflip():
   ret = {
      "game" : "coinflip",
   }

   ret["value"] = random.choice(["heads", "tails"])

   return ret


@app.route('/lower', methods=['GET'])
def lower():
   ret = {
      "game" : "lower",
   }

   ret["value"] = random.randint(0, 100)

   return ret


@app.errorhandler(404)
def page_not_found(error):
   ret = {
      "error" : "Invalid Request"
   }

   return jsonify(ret)


if __name__ == '__main__':
   with open("secret_.key", "r") as f:
      app.secret_key = f.read()

   app.run()