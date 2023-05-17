from flask import request
from flask_sqlalchemy import SQLAlchemy
from jwts import create_jwt_token, get_username_from_token

from markupsafe import escape
import bcrypt

from utils import jsonret
import os

# pylint: disable-next=E0611
from __main__ import app
from database import User, db


def check_login(username: str | None, password: str | None) -> User | None:
    """
    Validates login given username and password

    Args:
        username (str): Username to login with
        password (str): Password to login with

    Returns:
        (str | None) : Returns user object if valid login, None otherwise.
    """
    if not (username or password):
        return None

    user = User.query.filter_by(username=username).first()

    if user and user.verify_password(password):
        return user

    return None


@app.route("/login", methods=["GET"])
@jsonret
def login():
    """
    Route to login. Takes username and password, returns
    session token to be used with rest of api.
    """

    username = request.values.get("username")
    password = request.values.get("password")

    user = check_login(username, password)
    if user:
        token = create_jwt_token(user.username)
        ret = {"login": True, "message": "Login Successful", "token": token}
    else:
        ret = {"login": False, "message": "Invalid username or password."}

    return ret


@app.route("/signup", methods=["GET"])
@jsonret
def signup():
    """
    Route to signup. Takes username and password, returns
    success message if login is successful.
    """
    username = request.values.get("username")
    password = request.values.get("password")

    if not (username or password):
        ret = {"login": False, "message": "Invalid username or password."}
        return ret

    user = User(username, password)
    # If User with username already exists, invalid
    if User.query.filter_by(username=username).first():
        ret = {"login": False, "message": "User already exists. Try logging in."}
        return ret

    # User does not exist, username and password provided
    db.session.add(user)
    db.session.commit()

    ret = {
        "login": True,
        "message": f"Successfully created account with username {escape(username)}",
    }
    return ret


@app.route("/me", methods=["GET"])
@jsonret
def me():
    """
    Returns information about current user.
    """

    token = request.values.get("token")
    username = get_username_from_token(token)

    if not username:
        ret = {"error": "Token invalid or not provided"}
        return ret


    user = User.query.filter_by(username=username).first()
    if not user:
        ret = {"error": "Token invalid or not provided"}
        return ret

    # Convert user object to JSON
    user_data = {
        "username": user.username,
        "money": user.money,
        "assets": user.assets,
    }

    return user_data