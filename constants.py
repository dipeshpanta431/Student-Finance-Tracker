INCOME_CATEGORIES = [
    ("Pocket Money", "Pocket Money"),
    ("Salary", "Salary"),
    ("Scholarship", "Scholarship"),
    ("Freelance", "Freelance"),
    ("Gift", "Gift"),
    ("Refund", "Refund"),
    ("Investment", "Investment"),
    ("Other", "Other")
]

EXPENSE_CATEGORIES = [
    ("Food", "Food"),
    ("Transportation", "Transportation"),
    ("Education", "Education"),
    ("Shopping", "Shopping"),
    ("Entertainment", "Entertainment"),
    ("Medical", "Medical"),
    ("Rent", "Rent"),
    ("Other", "Other")
]
ALL_CATEGORIES = list(
    dict(INCOME_CATEGORIES + EXPENSE_CATEGORIES).items()
)