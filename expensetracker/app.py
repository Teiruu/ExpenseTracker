from base import db
from flask import Flask, url_for, render_template, redirect, request
from model import Expense, AddExpense, AddIncome, Income
from pytz import timezone, UTC
from sqlalchemy import func

app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)
app.config.from_pyfile('instance/config.py')
with app.app_context():
    db.create_all()
    db.session.commit()


def convert_to_local(utc_dt):
    london_tz = timezone('Europe/London')
    return utc_dt.replace(tzinfo=UTC).astimezone(london_tz)


@app.route('/', methods=["GET"])
def expense_list():
    incomes = Income.query.all()
    expenses = Expense.query.all()
    total_income = db.session.query(func.sum(Income.amount)).scalar() or 0
    total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
    balance = total_income - total_expenses

    # Convert datetimes to local time
    for income in incomes:
        income.created_at = convert_to_local(income.created_at)
    for expense in expenses:
        expense.created_at = convert_to_local(expense.created_at)

    return render_template("index.html", expenses=expenses, incomes=incomes, total_income=total_income,
                           total_expenses=total_expenses,
                           balance=balance)

@ app.route('/add_expense', methods=["GET", "POST"])
def add_expense():
    form = AddExpense()
    if form.validate_on_submit():
        create_expense = Expense(
            category=form.category.data)
        create_expense.set_amount(form.amount.data)
        # Adding the task to the list
        db.session.add(create_expense)
        db.session.commit()
        return redirect(url_for('expense_list'))
    return render_template("add_expense.html", form=form)


@app.route('/edit/expense/<int:expense_id>', methods=["GET", "POST"])
def edit_expense(expense_id):
    expense = db.get_or_404(Expense, expense_id)

    if request.method == "POST":
        expense.category = request.form["category"]
        expense.set_amount(float(request.form["amount"]))  # ← convert input string to float
        db.session.commit()
        return redirect(url_for("expense_list"))

    return render_template("edit_expense.html", expense=expense)


@app.route('/delete/expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    # remove expense by ID
    expense = db.get_or_404(Expense, expense_id)

    if request.method == "POST":
        db.session.delete(expense)
        db.session.commit()
        return redirect(url_for("expense_list"))

    return render_template("index.html", expense=expense)


@app.route('/add_income', methods=["GET", "POST"])
def add_income():
    form = AddIncome()
    if form.validate_on_submit():
        create_income = Income(
            category=form.category.data)
        create_income.set_amount(form.amount.data)
        # Adding the task to the list
        db.session.add(create_income)
        db.session.commit()
        return redirect(url_for('expense_list'))
    return render_template("add_income.html", form=form)


@app.route('/edit/income/<int:income_id>', methods=["GET", "POST"])
def edit_income(income_id):
    income = db.get_or_404(Income, income_id)

    if request.method == "POST":
        income.category = request.form["category"]
        income.set_amount(float(request.form["amount"]))  # ← convert input string to float
        db.session.commit()
        return redirect(url_for("expense_list"))

    return render_template("edit_income.html", income=income)


@app.route('/delete/income/<int:income_id>', methods=['POST'])
def delete_income(income_id):
    # remove income by ID
    income = db.get_or_404(Income, income_id)

    if request.method == "POST":
        db.session.delete(income)
        db.session.commit()
        return redirect(url_for("expense_list"))

    return render_template("index.html", income=income)
