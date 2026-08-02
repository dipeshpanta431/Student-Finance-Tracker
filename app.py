from flask import Flask, render_template, redirect, url_for, flash
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Transaction
from forms import RegistrationForm, LoginForm, TransactionForm

app = Flask(__name__)

# ----------------------------
# Configuration
# ----------------------------
app.config["SECRET_KEY"] = "your-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense_tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ----------------------------
# Flask-Login
# ----------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
    # If using an older SQLAlchemy version, you can keep:
    # return User.query.get(int(user_id))


# ----------------------------
# Home
# ----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------
# Register
# ----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():

        existing_user = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_user:
            flash("Email already registered.", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(form.password.data)

        new_user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


# ----------------------------
# Login
# ----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and check_password_hash(
            user.password_hash,
            form.password.data
        ):

            login_user(user)

            flash("Login successful!", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


# ----------------------------
# Dashboard
# ----------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# ----------------------------
# Add Transaction
# ----------------------------
@app.route("/add_transaction", methods=["GET", "POST"])
@login_required
def add_transaction():

    form = TransactionForm()

    if form.validate_on_submit():

        transaction = Transaction(
            amount=form.amount.data,
            transaction_type=form.transaction_type.data,
            category=form.category.data,
            payment_mode=form.payment_mode.data,
            date=form.date.data,
            description=form.description.data,
            user_id=current_user.id
        )

        db.session.add(transaction)
        db.session.commit()

        flash("Transaction added successfully!", "success")

        return redirect(url_for("dashboard"))

    return render_template(
        "add_transaction.html",
        form=form
    )


# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)