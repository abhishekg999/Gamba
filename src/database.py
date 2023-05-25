from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
import bcrypt
import os
from redis_server import create_redis_lock
from sqlalchemy.ext.mutable import MutableDict


# pylint: disable-next=E0611
from __main__ import app

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

db = SQLAlchemy()
db.init_app(app)

DB_LOCK = create_redis_lock("DB_LOCK")

with app.app_context():
    Session = sessionmaker(db.engine)

class User(db.Model):
    """
    SQLAlchemy Database connector for User object.

    User fields:
        - id
        - username
        - password
        - money
        - assets
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    money = db.Column(
        db.Numeric(precision=38, scale=2), nullable=False, server_default="0.00"
    )
    assets = db.Column(
        MutableDict.as_mutable(db.JSON), nullable=False, server_default="{}"
    )

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password: str):
        """
        Hashes and sets password hash to user object

        Args:
            password (str): Password to hash
        """
        self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password)


with app.app_context():
    db.create_all()
