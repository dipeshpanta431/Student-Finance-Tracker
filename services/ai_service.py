import os

from dotenv import load_dotenv

try:
    from google import genai
except ImportError:
    genai = None

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def ask_gemini(prompt: str) -> str:
    """
    Sends a prompt to Gemini and returns the response.
    """

    if genai is None:
        return (
            "AI insights are unavailable because the Google GenAI package is not "
            "installed. Run: python -m pip install -r requirements.txt"
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "AI insights are unavailable because GEMINI_API_KEY is not configured."

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        return response.text or "The AI service returned an empty response."
    except Exception:
        return "AI insights are temporarily unavailable. Please try again later."

from collections import defaultdict


def build_financial_summary(transactions):

    total_income = 0
    total_expense = 0

    income_categories = defaultdict(float)
    expense_categories = defaultdict(float)

    payment_modes = defaultdict(int)

    recent_transactions = []

    for transaction in transactions:

        if transaction.transaction_type == "Income":

            total_income += transaction.amount
            income_categories[transaction.category] += transaction.amount

        else:

            total_expense += transaction.amount
            expense_categories[transaction.category] += transaction.amount

        if transaction.payment_mode:
            payment_modes[transaction.payment_mode] += 1

        recent_transactions.append({
            "date": str(transaction.date),
            "category": transaction.category,
            "type": transaction.transaction_type,
            "amount": transaction.amount
        })

    highest_income = (
        max(income_categories.items(), key=lambda x: x[1])
        if income_categories else ("None", 0)
    )

    highest_expense = (
        max(expense_categories.items(), key=lambda x: x[1])
        if expense_categories else ("None", 0)
    )

    return {

        "total_income": total_income,

        "total_expense": total_expense,

        "balance": total_income - total_expense,

        "highest_income": highest_income,

        "highest_expense": highest_expense,

        "payment_modes": dict(payment_modes),

        "recent_transactions": recent_transactions[-5:]
    }

def generate_monthly_summary(summary):

    prompt = f"""
You are an AI Financial Advisor.

Generate a concise monthly financial summary.

Maximum 80 words.

Financial Data

Income:
NPR {summary['total_income']:.2f}

Expense:
NPR {summary['total_expense']:.2f}

Balance:
NPR {summary['balance']:.2f}

Highest Expense:
{summary['highest_expense'][0]}
NPR {summary['highest_expense'][1]:.2f}

Return only:

• Summary

• Key Findings

• Recommendation
"""

    return ask_gemini(prompt)

def generate_saving_tips(summary):

    prompt = f"""
You are a financial advisor.

Based ONLY on this financial summary,
give exactly 3 saving tips.

Maximum 60 words.

Income:
NPR {summary['total_income']:.2f}

Expense:
NPR {summary['total_expense']:.2f}

Highest Expense:
{summary['highest_expense'][0]}
NPR {summary['highest_expense'][1]:.2f}
"""

    return ask_gemini(prompt)

def generate_budget_recommendation(summary):

    prompt = f"""
Recommend next month's budget.

Keep the response under 80 words.

Income:
NPR {summary['total_income']:.2f}

Expense:
NPR {summary['total_expense']:.2f}

Highest Expense:
{summary['highest_expense'][0]}
"""
    return ask_gemini(prompt)

def generate_spending_analysis(summary):

    prompt = f"""
Analyze spending behaviour.

Maximum 80 words.

Income:
NPR {summary['total_income']:.2f}

Expense:
NPR {summary['total_expense']:.2f}

Highest Expense:
{summary['highest_expense'][0]}
"""
    return ask_gemini(prompt)


def generate_overspending_alert(summary):

    prompt = f"""
Identify whether the user appears to be overspending.

Maximum 60 words.

Income:
NPR {summary['total_income']:.2f}

Expense:
NPR {summary['total_expense']:.2f}

Highest Expense:
{summary['highest_expense'][0]}
"""

    return ask_gemini(prompt)
