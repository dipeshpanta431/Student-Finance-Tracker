from datetime import date

def get_budget_status(percentage):

    if percentage < 80:
        return "On Track", "bg-success"

    elif percentage <= 100:
        return "Near Limit", "bg-warning"

    return "Over Budget", "bg-danger"


def calculate_budget_progress(budget_amount, expense):

    if budget_amount <= 0:
        return 0, 0

    percentage = (expense / budget_amount) * 100

    progress_width = min(percentage, 100)

    return percentage, progress_width


def calculate_dashboard_totals(transactions):

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

    return total_income, total_expense, balance


def prepare_category_chart_data(expense_by_category):

    labels = [item.category for item in expense_by_category]

    totals = [float(item.total) for item in expense_by_category]

    return labels, totals
def get_budget_status(percentage):

    if percentage < 80:
        return "On Track", "bg-success"

    elif percentage <= 100:
        return "Near Limit", "bg-warning"

    else:
        return "Over Budget", "bg-danger"

def get_budget_message(
    budget_amount,
    current_month_expense,
    remaining_budget
):

    if budget_amount == 0:
        return "Set a budget to start tracking your monthly spending."

    if remaining_budget > 0:
        return (
            f"You still have NPR {remaining_budget:,.2f} "
            "remaining this month."
        )

    if remaining_budget == 0:
        return "You've exactly reached your monthly budget."

    return (
        f"You have exceeded your budget by "
        f"NPR {abs(remaining_budget):,.2f}."
    )