from flask import Flask
from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

from utils import jsonret

load_dotenv()

# for AWS default configuration
application = Flask(__name__)
app = application

limiter = None

# pylint: disable=C0413, W0611
import database
import account
import games
import stocks

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
