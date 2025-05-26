from datetime import datetime
from flask_wtf import FlaskForm
from sqlalchemy.orm import Mapped, mapped_column
from wtforms import StringField, DecimalField
from wtforms.validators import DataRequired
from sqlalchemy import Integer, String, DateTime

from base import db


# Class to make the database Expense
class Expense(db.Model):
    expense_id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())

    def set_amount(self, pounds):
        self.amount = int(pounds * 100)
    def get_amount(self):
        return self.amount / 100

# Class for add expense form
class AddExpense(FlaskForm):
    category = StringField('category', validators=[DataRequired()])
    amount = DecimalField('amount', places=2, validators=[DataRequired()])

# Class to make the database Income
class Income(db.Model):
    income_id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())

    def set_amount(self, pounds):
        self.amount = int(pounds * 100)
    def get_amount(self):
        return self.amount / 100

# Class for add expense form
class AddIncome(FlaskForm):
    amount = DecimalField('amount', places=2, validators=[DataRequired()])