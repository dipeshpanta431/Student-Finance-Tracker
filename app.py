from datetime import datetime,date
from collections import defaultdict
from calendar import monthrange     

import csv
from io import StringIO

from flask import Flask, render_template, redirect, request, url_for, flash, Response
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from helpers import calculate_budget_progress, calculate_dashboard_totals, get_budget_message, get_budget_status, prepare_category_chart_data
from models import Budget, db, User, Transaction
from forms import RegistrationForm, LoginForm, TransactionForm, BudgetForm
from sqlalchemy import or_, func
from constants import (
    INCOME_CATEGORIES,
    EXPENSE_CATEGORIES,
    ALL_CATEGORIES
)
from io import BytesIO

from flask import send_file

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
app = Flask(__name__)

# ----------------------------
# Configuration
# ----------------------------
app.config["SECRET_KEY"] = "your-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance_tracker.db"
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
    budget_form = BudgetForm()
    search = request.args.get("search", "")
    scroll_position = request.args.get("scroll_position", "0")
    transaction_type = request.args.get("type", "")
    category = request.args.get("category", "")
    payment_mode = request.args.get("payment_mode", "")
    from_date = request.args.get("from_date", "")
    to_date = request.args.get("to_date", "")  


    transactions = Transaction.query.filter_by(
        user_id=current_user.id
    )
    all_transactions = Transaction.query.filter_by(
        user_id=current_user.id
    )
    if search:
        transactions = transactions.filter(
            or_(
                Transaction.category.ilike(f"%{search}%"),
                Transaction.description.ilike(f"%{search}%"),
                Transaction.custom_category.ilike(f"%{search}%"),
                Transaction.payment_mode.ilike(f"%{search}%")
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
    from_date_obj = None
    to_date_obj = None

    if from_date:
        from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()

    if to_date:
        to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()

    if from_date_obj and to_date_obj and from_date_obj > to_date_obj:
        flash("From Date cannot be later than To Date.", "warning")
        return redirect(url_for("dashboard"))

    if from_date_obj:
        transactions = transactions.filter(
            Transaction.date >= from_date_obj
        )

    if to_date_obj:
        transactions = transactions.filter(
            Transaction.date <= to_date_obj
        )

    expense_by_category = (
        transactions
        .filter(Transaction.transaction_type == "Expense")
        .with_entities(
            Transaction.category,
            func.sum(Transaction.amount).label("total")
        )
        .group_by(Transaction.category)
        .all()
    )
    income_by_category = (
        transactions
        .filter(Transaction.transaction_type == "Income")
        .with_entities(
            Transaction.category,
            func.sum(Transaction.amount).label("total")
        )
        .group_by(Transaction.category)
        .all()
    )
    category_labels, category_totals = \
        prepare_category_chart_data(expense_by_category)

    income_category_labels, income_category_totals = \
        prepare_category_chart_data(income_by_category)

    transactions = transactions.order_by(
        Transaction.date.desc()
    ).all()


    total_income, total_expense, balance = \
    calculate_dashboard_totals(all_transactions)

   
    if transaction_type == "Income":
        categories = INCOME_CATEGORIES

    elif transaction_type == "Expense":
        categories = EXPENSE_CATEGORIES

    else:
        categories = ALL_CATEGORIES

    current_month = date.today().replace(day=1)
    daily_income = defaultdict(float)
    daily_expense = defaultdict(float)

    for transaction in transactions:

        if (
            transaction.date.year == current_month.year and
            transaction.date.month == current_month.month
        ):

            day = transaction.date.day

            if transaction.transaction_type == "Income":
                daily_income[day] += float(transaction.amount)

            else:
                daily_expense[day] += float(transaction.amount)

    days_in_month = monthrange(
        current_month.year,
        current_month.month
    )[1]

    daily_labels = list(range(1, days_in_month + 1))

    daily_income_data = [
        daily_income.get(day, 0)
        for day in daily_labels
    ]

    daily_expense_data = [
        daily_expense.get(day, 0)
        for day in daily_labels
    ]
    current_budget = Budget.query.filter_by(
        user_id=current_user.id,
        budget_month=current_month
    ).first()
    current_month_expense = sum(

        transaction.amount

        for transaction in all_transactions

        if (
            transaction.transaction_type == "Expense"
            and transaction.date.year == current_month.year
            and transaction.date.month == current_month.month
        )

    )
    budget_amount = (
        current_budget.amount
        if current_budget
        else 0
    )

    remaining_budget = budget_amount - current_month_expense

    budget_percentage, progress_width = \
    calculate_budget_progress(
        budget_amount,
        current_month_expense
    )

    if budget_amount == 0:

        budget_status = "No Budget"
        progress_color = "bg-secondary"

    else:

        budget_status, progress_color = get_budget_status(
            budget_percentage
        )
    budget_message = get_budget_message(
    budget_amount,
    current_month_expense,
    remaining_budget
)
    if not budget_form.budget_month.data:
        budget_form.budget_month.data = datetime.today().strftime("%Y-%m")

    return render_template(
        "dashboard.html",
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        search=search,
        transaction_type=transaction_type,
        categories=categories,
        payment_modes=form.payment_mode.choices,
        payment_mode=payment_mode,
        from_date=from_date,
        to_date=to_date,
        category_labels=category_labels,
        category_totals=category_totals,
        income_categories=INCOME_CATEGORIES,
        expense_categories=EXPENSE_CATEGORIES,
        daily_labels=daily_labels,
        daily_income_data=daily_income_data,
        daily_expense_data=daily_expense_data,
        current_month=current_month,
        budget_form=budget_form,
        current_budget=current_budget,
        budget_amount=budget_amount,
        current_month_expense=current_month_expense,
        remaining_budget=remaining_budget,
        budget_percentage=budget_percentage,
        progress_width=progress_width,
        budget_status=budget_status,
        progress_color=progress_color,
        budget_message=budget_message,
        scroll_position=scroll_position,
        income_by_category=income_by_category,
        income_category_labels=income_category_labels,
    income_category_totals=income_category_totals
      
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
            custom_category=(
                form.custom_category.data.strip()
                if form.category.data == "Other"
                and form.custom_category.data
                else None
            ),
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
    button_text="Save Transaction",
    income_categories=INCOME_CATEGORIES,
    expense_categories=EXPENSE_CATEGORIES
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
        transaction.custom_category = (
            form.custom_category.data.strip()
            if form.category.data == "Other"
            and form.custom_category.data
            else None
        )

        db.session.commit()

        flash("Transaction updated successfully!", "success")

        return redirect(url_for("dashboard"))
    return render_template(
    "add_transaction.html",
    form=form,
    title="Edit Transaction",
    button_text="Save Changes",
    income_categories=INCOME_CATEGORIES,
    expense_categories=EXPENSE_CATEGORIES
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
#---------------
#Budget
#---------------
@app.route("/budget/save", methods=["POST"])
@login_required
def save_budget():

    form = BudgetForm()

    if form.validate_on_submit():

        budget_date = datetime.strptime(
            form.budget_month.data,
            "%Y-%m"
        ).date().replace(day=1)

        existing_budget = Budget.query.filter_by(
            user_id=current_user.id,
            budget_month=budget_date
        ).first()

        if existing_budget:

            existing_budget.amount = form.amount.data

            flash(
                "Budget updated successfully!",
                "success"
            )

        else:

            budget = Budget(

                budget_month=budget_date,

                amount=form.amount.data,

                user_id=current_user.id

            )

            db.session.add(budget)

            flash(
                "Budget created successfully!",
                "success"
            )

        db.session.commit()

    return redirect(url_for("dashboard"))

#-----------------
#Export CSV
#-----------------
@app.route("/transactions/export")
@login_required
def export_transactions():
    search = request.args.get("search", "")
    transaction_type = request.args.get("type", "")
    category = request.args.get("category", "")
    payment_mode = request.args.get("payment_mode", "")
    from_date = request.args.get("from_date", "")
    to_date = request.args.get("to_date", "")

    transactions = Transaction.query.filter_by(
        user_id=current_user.id
    )

    if search:
        transactions = transactions.filter(
            or_(
                Transaction.category.ilike(f"%{search}%"),
                Transaction.description.ilike(f"%{search}%"),
                Transaction.custom_category.ilike(f"%{search}%"),
                Transaction.payment_mode.ilike(f"%{search}%")
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

    if from_date:
        from_date_obj = datetime.strptime(
            from_date,
            "%Y-%m-%d"
        ).date()

        transactions = transactions.filter(
            Transaction.date >= from_date_obj
        )

    if to_date:
        to_date_obj = datetime.strptime(
            to_date,
            "%Y-%m-%d"
        ).date()

        transactions = transactions.filter(
            Transaction.date <= to_date_obj
        )

    transactions = transactions.order_by(
        Transaction.date.desc()
    ).all()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Date",
        "Type",
        "Category",
        "Amount",
        "Payment Mode",
        "Description"
    ])

    for transaction in transactions:

        if (
            transaction.category == "Other"
            and transaction.custom_category
        ):
            category_name = transaction.custom_category
        else:
            category_name = transaction.category

        writer.writerow([
            transaction.date,
            transaction.transaction_type,
            category_name,
            transaction.amount,
            transaction.payment_mode,
            transaction.description or ""
        ])

    response = Response(
        output.getvalue(),
        mimetype="text/csv"
    )

    response.headers["Content-Disposition"] = (
        "attachment; filename=expense_transactions.csv"
    )

    return response



# -----------------
# Reports
# -----------------
@app.route("/reports")
@login_required
def reports():

    current_date = datetime.now()

    selected_month = request.args.get(
        "month",
        current_date.month,
        type=int
    )

    selected_year = request.args.get(
        "year",
        current_date.year,
        type=int
    )
    start_date = date(
    selected_year,
    selected_month,
    1
    )

    if selected_month == 12:
        end_date = date(
            selected_year + 1,
            1,
            1
        )
    else:
        end_date = date(
            selected_year,
            selected_month + 1,
            1
    )
    monthly_transactions = Transaction.query.filter(
    Transaction.user_id == current_user.id,
    Transaction.date >= start_date,
    Transaction.date < end_date
    )

    monthly_income = (
        monthly_transactions
        .filter(Transaction.transaction_type == "Income")
        .with_entities(
            func.sum(Transaction.amount)
        )
        .scalar()
        or 0
    )

    monthly_expense = (
        monthly_transactions
        .filter(Transaction.transaction_type == "Expense")
        .with_entities(
            func.sum(Transaction.amount)
        )
        .scalar()
        or 0
    )
    payment_mode_analysis = (
        monthly_transactions
        .filter(Transaction.transaction_type == "Expense")
        .with_entities(
            Transaction.payment_mode,
            func.sum(Transaction.amount)
        )
        .group_by(Transaction.payment_mode)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
    
    top_expense_categories = (
        monthly_transactions
        .filter(
            Transaction.transaction_type == "Expense"
        )
        .with_entities(
            func.coalesce(
                Transaction.custom_category,
                Transaction.category
            ).label("category_name"),

            func.sum(Transaction.amount).label("total")
        )
        .group_by(
            func.coalesce(
                Transaction.custom_category,
                Transaction.category
            )
        )
        .order_by(
            func.sum(Transaction.amount).desc()
        )
        .limit(5)
        .all()
    )
    top_income_categories = (
        monthly_transactions
        .filter(
            Transaction.transaction_type == "Income"
        )
        .with_entities(
            func.coalesce(
                Transaction.custom_category,
                Transaction.category
            ).label("category_name"),

            func.sum(Transaction.amount).label("total")
        )
        .group_by(
            func.coalesce(
                Transaction.custom_category,
                Transaction.category
            )
        )
        .order_by(
            func.sum(Transaction.amount).desc()
        )
        .limit(5)
        .all()
    )
    total_payment_mode_expense = sum(
        total for _, total in payment_mode_analysis
    )
    payment_mode_insights = []

    for payment_mode, total in payment_mode_analysis:

        percentage = (
            (total / total_payment_mode_expense) * 100
            if total_payment_mode_expense > 0
            else 0
        )

        payment_mode_insights.append(
            (payment_mode, total, percentage)
        )
    months = [
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December")
    ]

    years = list(range(
        current_date.year - 5,
        current_date.year + 1
    ))

    return render_template(
        "reports.html",
        months=months,
        years=years,
        selected_month=selected_month,
        selected_year=selected_year,
        monthly_income=monthly_income,
        monthly_expense=monthly_expense,
        top_expense_categories=top_expense_categories,
        top_income_categories=top_income_categories,
        payment_mode_analysis=payment_mode_analysis,
        payment_mode_insights=payment_mode_insights,
        current_date=current_date
        
    )

# ------------
# Reports
# ------------

@app.route("/reports/pdf")
@login_required
def download_report():

    current_date = datetime.now()

    # Selected month and year
    selected_month = request.args.get(
        "month",
        current_date.month,
        type=int
    )

    selected_year = request.args.get(
        "year",
        current_date.year,
        type=int
    )

    # Validate month
    if selected_month < 1 or selected_month > 12:
        selected_month = current_date.month

    # Validate year
    if selected_year < 2000 or selected_year > current_date.year:
        selected_year = current_date.year

    # Report date range
    start_date = date(
        selected_year,
        selected_month,
        1
    )

    if selected_month == 12:
        end_date = date(
            selected_year + 1,
            1,
            1
        )
    else:
        end_date = date(
            selected_year,
            selected_month + 1,
            1
        )

    # Monthly transactions
    monthly_transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date < end_date
    )

    # --------------------
    # Total Income
    # --------------------

    monthly_income = (
        monthly_transactions
        .filter(
            Transaction.transaction_type == "Income"
        )
        .with_entities(
            func.sum(Transaction.amount)
        )
        .scalar()
        or 0
    )

    # --------------------
    # Total Expense
    # --------------------

    monthly_expense = (
        monthly_transactions
        .filter(
            Transaction.transaction_type == "Expense"
        )
        .with_entities(
            func.sum(Transaction.amount)
        )
        .scalar()
        or 0
    )

    # --------------------
    # Balance
    # --------------------

    monthly_balance = monthly_income - monthly_expense

    # --------------------
    # Payment Mode Analysis
    # --------------------

    payment_mode_analysis = (
        monthly_transactions
        .filter(
            Transaction.transaction_type == "Expense"
        )
        .with_entities(
            Transaction.payment_mode,
            func.sum(Transaction.amount)
        )
        .group_by(
            Transaction.payment_mode
        )
        .order_by(
            func.sum(Transaction.amount).desc()
        )
        .all()
    )

    total_payment_mode_expense = sum(
        total for _, total in payment_mode_analysis
    )

    payment_mode_insights = []

    for payment_mode, total in payment_mode_analysis:

        percentage = (
            (total / total_payment_mode_expense) * 100
            if total_payment_mode_expense > 0
            else 0
        )

        payment_mode_insights.append(
            (
                payment_mode or "Unknown",
                total,
                percentage
            )
        )

    # --------------------
    # Top Expense Categories
    # --------------------

    top_expense_categories = (
        monthly_transactions
        .filter(
            Transaction.transaction_type == "Expense"
        )
        .with_entities(
            func.coalesce(
                Transaction.custom_category,
                Transaction.category
            ).label("category_name"),

            func.sum(Transaction.amount).label("total")
        )
        .group_by(
            func.coalesce(
                Transaction.custom_category,
                Transaction.category
            )
        )
        .order_by(
            func.sum(Transaction.amount).desc()
        )
        .limit(5)
        .all()
    )
    # --------------------
    # Top Income Categories
    # --------------------

    top_income_categories = (
        monthly_transactions
        .filter(
            Transaction.transaction_type == "Income"
        )
        .with_entities(
            func.coalesce(
                Transaction.custom_category,
                Transaction.category
            ).label("category_name"),

            func.sum(Transaction.amount).label("total")
        )
        .group_by(
            func.coalesce(
                Transaction.custom_category,
                Transaction.category
            )
        )
        .order_by(
            func.sum(Transaction.amount).desc()
        )
        .limit(5)
        .all()
    )

    # --------------------
    # Month Name
    # --------------------

    month_name = datetime(
        selected_year,
        selected_month,
        1
    ).strftime("%B")

    # --------------------
    # Create PDF
    # --------------------

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        title=f"Financial Report - {month_name} {selected_year}"
    )

    styles = getSampleStyleSheet()

    elements = []

    # --------------------
    # Title
    # --------------------

    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.styles import ParagraphStyle

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=24,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Heading2"],
        alignment=TA_CENTER,
        fontSize=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=20,
    )

    elements.append(
        Paragraph(
            "Student Finance Tracker",
            title_style
        )
    )

    elements.append(
        Paragraph(
            "Financial Report",
            subtitle_style
        )
    )
    elements.append(
        Spacer(1, 20)
    )
    # --------------------
    # Report Information
    # --------------------

    info_data = [

        ["Name", current_user.full_name],

        ["Email", current_user.email],

        ["Report Period", f"{month_name} {selected_year}"],

        ["Generated On", current_date.strftime("%d %B %Y")]

    ]

    info_table = Table(
        info_data,
        colWidths=[120, 280]
    )

    info_table.setStyle(

        TableStyle([

            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#f1f5f9")),

            ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#334155")),

            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),

            ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#d1d5db")),

            ("BOTTOMPADDING", (0,0), (-1,-1), 8),

            ("TOPPADDING", (0,0), (-1,-1), 8),

            ("LEFTPADDING", (0,0), (-1,-1), 8),

            ("RIGHTPADDING", (0,0), (-1,-1), 8),

        ])

    )

    elements.append(info_table)

    elements.append(
        Spacer(1,20)
    )

    # --------------------
    # Financial Summary Table
    # --------------------

    summary_data = [

        ["Item", "Value"],

        ["Report Period", f"{month_name} {selected_year}"],

        ["Total Income", f"NPR {monthly_income:,.2f}"],

        ["Total Expense", f"NPR {monthly_expense:,.2f}"],

        [
            "Net Cash Flow",
            f"NPR {monthly_balance:,.2f}"
        ],

        [
            "Highest Expense Category",
            top_expense_categories[0][0]
            if top_expense_categories
            else "No data"
        ],

        [
            "Top Income Category",
            top_income_categories[0][0]
            if top_income_categories
            else "No data"
        ],

        [
            "Most Used Payment Mode",
            payment_mode_insights[0][0]
            if payment_mode_insights
            else "No data"
        ]

    ]

    summary_table = Table(
        summary_data,
        colWidths=[180, 220]
    )

    summary_table.setStyle(

        TableStyle([

            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1e40af")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),

            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

           ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#d1d5db")),

            ("BACKGROUND", (0,1), (-1,-1), colors.whitesmoke),

            ("ROWBACKGROUNDS",
                (0,1),
                (-1,-1),
                [colors.white, colors.HexColor("#f8fafc")]
            ),

            ("BOTTOMPADDING", (0,0), (-1,0), 10),

            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),

        ])

    )

    elements.append(summary_table)

    elements.append(
        Spacer(1,20)
    )

    # --------------------
    # Payment Mode Breakdown
    # --------------------

    elements.append(
        Paragraph(
            "Payment Mode Analysis",
            styles["Heading2"]
        )
    )

    elements.append(
        Spacer(1,10)
    )

    if payment_mode_insights:

        for payment_mode, total, percentage in payment_mode_insights:

            elements.append(

                Paragraph(

                    f"<b>{payment_mode}</b> — "
                    f"NPR {total:,.2f} "
                    f"({percentage:.2f}%)",

                    styles["Normal"]

                )

            )

    else:

        elements.append(

            Paragraph(

                "No payment data found.",

                styles["Normal"]

            )

        )

    elements.append(
        Spacer(1,20)
    )


    elements.append(
        Paragraph(
            "<font color='#64748b'>"
            "Generated by Student Finance Tracker"
            "</font>",
            styles["Italic"]
        )
    )

    # --------------------
    # Build PDF
    # --------------------

    doc.build(elements)
    buffer.seek(0)

    # --------------------
    # Send PDF
    # --------------------
    return send_file(
        buffer,
        as_attachment=True,
        download_name=(
            f"Financial_Report_"
            f"{month_name}_"
            f"{selected_year}.pdf"
        ),
        mimetype="application/pdf"
    )
@app.route("/about")
def about():
    return render_template("about.html")
# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
