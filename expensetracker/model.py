from datetime import datetime
from flask_wtf import FlaskForm
from sqlalchemy.orm import Mapped, mapped_column
from wtforms import StringField, DecimalField
from wtforms.fields.datetime import DateField
from wtforms.validators import DataRequired, Optional
from sqlalchemy import String, DateTime
from base import db


class Expense(db.Model):
    """
    SQLAlchemy model for storing expense records.
    Each expense has a category, an amount (stored as integer pennies), and a timestamp.
    """
    # Primary key for the expense table
    expense_id: Mapped[int] = mapped_column(primary_key=True)
    # Category of the expense (e.g., 'food', 'utilities')
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    # Amount stored as integer pennies to avoid floating-point rounding issues
    amount: Mapped[int] = mapped_column()
    # Timestamp when the record was created; defaults to the current UTC time
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())

    def set_amount(self, pounds):
        # Multiply by 100 and convert to int for storage
        self.amount = int(pounds * 100)

    def get_amount(self):
        # Divide by 100 to convert pennies back to pounds
        return self.amount / 100


class AddExpense(FlaskForm):
    """
    WTForms form for adding a new expense via a Flask view.
    """
    # Category is required and limited to a string field
    category = StringField('category', validators=[DataRequired()])
    # Amount is required; two decimal places for pounds and pence
    amount = DecimalField('amount', places=2, validators=[DataRequired()])


class Income(db.Model):
    """
    SQLAlchemy model for storing income records.
    Similar structure to Expense: category, amount, and timestamp.
    """
    # Primary key for the income table
    income_id: Mapped[int] = mapped_column(primary_key=True)
    # Category of the income (e.g., 'salary', 'interest')
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    # Amount stored as integer pennies
    amount: Mapped[int] = mapped_column()
    # Timestamp when the record was created; defaults to the current UTC time
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())

    def set_amount(self, pounds):
        """
        Set the amount in pounds as integer pennies.

        :param pounds: Monetary value in pounds (float or Decimal)
        """
        self.amount = int(pounds * 100)

    def get_amount(self):
        """
        Get the stored amount converted back to pounds.

        :return: Monetary value in pounds as float
        """
        return self.amount / 100


class AddIncome(FlaskForm):
    """
    WTForms form for adding a new income entry via a Flask view.
    """
    # Category is required
    category = StringField('category', validators=[DataRequired()])
    # Amount is required; stores two decimal places
    amount = DecimalField('amount', places=2, validators=[DataRequired()])


class FilterForm(FlaskForm):
    """
    WTForms form for filtering records by a date range.
    Both start_date and end_date are optional.
    """
    # Optional start date for filtering; expects DD-MM-YYYY format
    start_date = DateField('Start Date', format='%d-%m-%Y', validators=[Optional()])
    # Optional end date for filtering; expects DD-MM-YYYY format
    end_date = DateField('End Date', format='%d-%m-%Y', validators=[Optional()])
