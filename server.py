from flask import Flask
from flask import request, jsonify, flash
from flask import abort, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from markupsafe import escape
import json

import random
import sqlite3
from sqlite3 import Error

from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

from utils import jsonret

load_dotenv()

# for AWS default configuration
application = Flask(__name__)
app = application

limiter = Limiter(get_remote_address, app=app)

# pylint: disable=C0413, W0611
import account
import games

@app.errorhandler(404)
@jsonret
def page_not_found(error):
    """Invalid request"""
    ret = {"error": "Invalid Request"}

    return ret

@app.errorhandler(429) 
def handle_rate_limit_exceeded(error):
    response = jsonify({
        'error': 'Rate limit exceeded. Please try again later.'
    })
    return response

if __name__ == "__main__":
    app.secret_key = os.getenv("SECRET_KEY")
    app.run(debug=True)
