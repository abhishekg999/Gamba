import jwt
from datetime import datetime, timedelta

# pylint: disable-next=E0611
from __main__ import app

def create_jwt_token(username: str) -> str:
    """
    Creates JWT token given a username

    Args:
        username (str): Username to generate token for

    Returns:
        str: JWT token for user expiring in 1 day
    """
    payload = {"username": username, "exp": datetime.utcnow() + timedelta(minutes=15)}
    token = jwt.encode(
        payload=payload,
        key=app.config["SECRET_KEY"],
        algorithm="HS256",
    )

    return token

def validate_jwt_token(token: str) -> dict | None:
    """
    Validates JWT token and returns payload as dict.

    Args:
        token (str): JWT token

    Returns:
        dict | None: payload if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except:
        return None

def get_username_from_token(token):
    if not token:
        return None

    payload = validate_jwt_token(token)

    # if payload is None, invalid JWT
    if not payload:
        return None

    username = payload["username"]
    if not username:
        return None

    return username