from flask import Flask
from flask import request, jsonify, flash
from flask import abort, redirect, url_for

from markupsafe import escape
import json

import random
import sqlite3
from sqlite3 import Error

from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

# pylint: disable-next=C0413, W0611
import account
import games

@app.errorhandler(404)
def page_not_found(error):
    ret = {"error": "Invalid Request"}

    return jsonify(ret)


if __name__ == "__main__":
    app.secret_key = os.getenv("SECRET_KEY")
    app.run()
