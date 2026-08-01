from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

from flask_login import UserMixin
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id= db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100),nullable=False)

    email = db.Column(db.String(120),unique=True,nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.email}>"

class Transaction(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Float, nullable=False)

    transaction_type = db.Column(db.String(20), nullable=False)

    category = db.Column(db.String(50), nullable=False)

    payment_mode = db.Column(db.String(30), nullable=False)

    date = db.Column(db.Date, nullable=False)

    description = db.Column(db.String(255), nullable=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

transactions = db.relationship(
    "Transaction",
    backref="user",
    lazy=True
)

