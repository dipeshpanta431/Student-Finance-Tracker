from datetime import datetime,date

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship(
        "Transaction",
        backref="user",
        lazy=True
    )

    budgets = db.relationship(
        "Budget",
        backref="user",
        lazy=True
    )
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
    custom_category = db.Column(db.String(100), nullable=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

class Budget(db.Model):

    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)

    budget_month = db.Column(
        db.Date,
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )