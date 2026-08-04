from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Transaction
from forms import RegistrationForm, LoginForm, TransactionForm
from sqlalchemy import or_

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
# LOGOUT
# ----------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))


# ----------------------------
# Dashboard
# ----------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    form = TransactionForm()
    search = request.args.get("search", "")
    transaction_type = request.args.get("type", "")
    category = request.args.get("category", "")
    payment_mode = request.args.get("payment_mode", "")

    transactions = Transaction.query.filter_by(
        user_id=current_user.id
    )

    if search:
        transactions = transactions.filter(
            or_(
                Transaction.category.ilike(f"%{search}%"),
                Transaction.description.ilike(f"%{search}%")
            )
        )
    if transaction_type:
        transactions = transactions.filter(
            Transaction.transaction_type == transaction_type
        )
    if category:
        transactions = transactions.filter(
            Transaction.category == category
        )
    if payment_mode:
        transactions = transactions.filter(
            Transaction.payment_mode == payment_mode
        )
    transactions = transactions.order_by(
        Transaction.date.desc()
    ).all()

    total_income = sum(
        t.amount
        for t in transactions
        if t.transaction_type == "Income"
    )

    total_expense = sum(
        t.amount
        for t in transactions
        if t.transaction_type == "Expense"
    )

    balance = total_income - total_expense

    return render_template(
        "dashboard.html",
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        search=search,
        transaction_type=transaction_type,
        categories=form.category.choices,
        payment_modes=form.payment_mode.choices,
        payment_mode=payment_mode
    )

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
    form=form,
    title="Add Transaction",
    button_text="Save Transaction"
    )






# ----------------------------
# Edit Transactions
# ----------------------------
@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):

    transaction = Transaction.query.get_or_404(transaction_id)

    form = TransactionForm(obj=transaction)

    if form.validate_on_submit():

        transaction.amount = form.amount.data
        transaction.transaction_type = form.transaction_type.data
        transaction.category = form.category.data
        transaction.payment_mode = form.payment_mode.data
        transaction.date = form.date.data
        transaction.description = form.description.data

        db.session.commit()

        flash("Transaction updated successfully!", "success")

        return redirect(url_for("dashboard"))

    return render_template(
    "add_transaction.html",
    form=form,
    title="Edit Transaction",
    button_text="Save Changes"
)



# ----------------------------
# Delete Transactions
# ----------------------------
@app.route("/delete/<int:transaction_id>")
@login_required
def delete_transaction(transaction_id):

    transaction = Transaction.query.get_or_404(transaction_id)

    db.session.delete(transaction)
    db.session.commit()

    flash("Transaction deleted successfully!", "success")

    return redirect(url_for("dashboard"))




# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)