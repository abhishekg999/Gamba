from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy

from markupsafe import escape
import bcrypt

# pylint: disable-next=E0611
from __main__ import app

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///account.db"

db.init_app(app)

class User(db.Model):
    """
    SQLAlchemy Database connector for User object. 

    User fields:
        - id
        - username
        - password
        - money 
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    money = db.Column(db.Numeric(precision=38, scale=2), nullable=False, server_default='0.00')

    def __init__(self, username, password):
        self.username = username 
        self.set_password(password)

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password)


with app.app_context():
    db.create_all()

def check_login(username: str | None, password: str | None) -> (User | None):
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
def login():
    """
    Route to login. Takes username and password, returns
    session token to be used with rest of api.
    """
    
    username = request.values.get("username")
    password = request.values.get("password")

    user = check_login(username, password)
    if user:
        print(user)
        ret = {"login": True, "message": "Login Successful"}
    else:
        ret = {"login": False, "message": "Invalid username or password."}

    return jsonify(ret)

@app.route("/signup", methods=["GET"])
def signup():
    """
    Route to signup. Takes username and password, returns
    success message if login is successful.
    """
    username = request.values.get("username")
    password = request.values.get("password")
    
    if not (username or password):
        ret = {"login": False, "message": "Invalid username or password."}
        return jsonify(ret)
    
    user = User(username, password)
    # If User with username already exists, invalid
    if User.query.filter_by(username=username).first():
        ret = {"login": False, "message": "User already exists. Try logging in."}
        return jsonify(ret)
     
    # User does not exist, username and password provided
    db.session.add(user)
    db.session.commit()

    ret = {"login": True, "message": f"Successfully created account with username {escape(username)}"}
    return jsonify(ret)
