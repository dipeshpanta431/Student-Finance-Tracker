from constants import INCOME_CATEGORIES, EXPENSE_CATEGORIES
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    FloatField,
    SelectField,
    DateField,
    TextAreaField,
    ValidationError
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange
)

class RegistrationForm(FlaskForm):

    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(min=3, max=100)
        ]
    )

    email = StringField(
    "Email",
    validators=[
        DataRequired(message="Email is required."),
        Email(message="Please enter a valid email address (e.g., example@gmail.com)")
    ]
)

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match.")
        ]
    )

    submit = SubmitField("Register")

class LoginForm(FlaskForm):

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Please enter a valid email address.")
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required.")
        ]
    )

    submit = SubmitField("Login")


class TransactionForm(FlaskForm):

    amount = FloatField(
        "Amount",
        validators=[
            DataRequired(message="Amount is required."),
            NumberRange(
                min=0.01,
                message="Amount must be greater than 0."
            )
        ]
    )

    transaction_type = SelectField(
        "Transaction Type",
        choices=[
            ("Income", "Income"),
            ("Expense", "Expense")
        ],
        validators=[DataRequired()]
    )

    category = SelectField(
        "Category",
        choices=INCOME_CATEGORIES + EXPENSE_CATEGORIES,
        validators=[DataRequired()]
    )

    payment_mode = SelectField(
        "Payment Mode",
        choices=[
            ("Cash", "Cash"),
            ("eSewa", "eSewa"),
            ("Khalti", "Khalti"),
            ("Bank Transfer", "Bank Transfer"),
            ("Debit Card", "Debit Card"),
            ("Credit Card", "Credit Card")
        ],
        validators=[DataRequired()]
    )

    date = DateField(
        "Date",
        format="%Y-%m-%d",
        validators=[DataRequired()]
    )

    description = TextAreaField(
        "Description",
        validators=[
            Length(
                max=255,
                message="Description cannot exceed 255 characters."
            )
        ]
    )
    custom_category = StringField(
        "Specify Category",
        validators=[Optional(), Length(max=100)]
    )

    submit = SubmitField("Save Transaction")
    def validate_custom_category(self, field):

        if (
            self.category.data == "Other"
            and not (field.data and field.data.strip())
        ):
            raise ValidationError(
                "Please specify the category."
            )