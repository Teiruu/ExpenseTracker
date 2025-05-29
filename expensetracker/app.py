from flask import Flask, url_for, render_template, redirect, request
from pytz import timezone, UTC
from sqlalchemy import func, desc
from base import db
from model import Expense, Income, AddExpense, AddIncome, FilterForm
import json


app = Flask(__name__)
app.config.from_pyfile('instance/config.py')  # Load additional config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
db.init_app(app)

# Ensure database tables are created on startup
with app.app_context():
    db.create_all()
    db.session.commit()


def convert_to_local(utc_dt):
    """
    Convert a UTC datetime to Europe/London timezone.

    :param utc_dt: A timezone-naive or UTC-aware datetime object.
    :return: A timezone-aware datetime in Europe/London.
    """
    london_tz = timezone('Europe/London')
    return utc_dt.replace(tzinfo=UTC).astimezone(london_tz)


@app.route('/', methods=['GET'])
def dashboard():
    """
    Display the dashboard with recent incomes and expenses, totals, and balance.
    Supports pagination (8 items per page).
    """
    # Retrieve and paginate recent records
    incomes = Income.query.order_by(desc(Income.created_at)).paginate(per_page=8)
    expenses = Expense.query.order_by(desc(Expense.created_at)).paginate(per_page=8)

    # Calculate totals
    total_income = db.session.query(func.sum(Income.amount)).scalar() or 0
    total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
    balance = total_income - total_expenses

    # Localize timestamps
    for record in (*incomes.items, *expenses.items):
        record.created_at = convert_to_local(record.created_at)

    return render_template(
        'index.html',
        incomes=incomes,
        expenses=expenses,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance
    )


@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    """
    Add a new expense record via form submission.
    """
    form = AddExpense()

    if form.validate_on_submit():
        expense = Expense(category=form.category.data)
        expense.set_amount(form.amount.data)
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('add_expense.html', form=form)


@app.route('/edit/expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    """
    Edit an existing expense identified by expense_id.
    """
    expense = db.get_or_404(Expense, expense_id)

    if request.method == 'POST':
        expense.category = request.form['category']
        expense.set_amount(float(request.form['amount']))
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit_expense.html', expense=expense)


@app.route('/delete/expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    """
    Delete an expense by its ID.
    """
    expense = db.get_or_404(Expense, expense_id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    """
    Add a new income record via form submission.
    """
    form = AddIncome()

    if form.validate_on_submit():
        income = Income(category=form.category.data)
        income.set_amount(form.amount.data)
        db.session.add(income)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('add_income.html', form=form)


@app.route('/edit/income/<int:income_id>', methods=['GET', 'POST'])
def edit_income(income_id):
    """
    Edit an existing income identified by income_id.
    """
    income = db.get_or_404(Income, income_id)

    if request.method == 'POST':
        income.category = request.form['category']
        income.set_amount(float(request.form['amount']))
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit_income.html', income=income)


@app.route('/delete/income/<int:income_id>', methods=['POST'])
def delete_income(income_id):
    """
    Delete an income by its ID.
    """
    income = db.get_or_404(Income, income_id)
    db.session.delete(income)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/view/incomes', methods=['GET', 'POST'])
def view_incomes():
    """
    View and filter all incomes by optional date range.
    """
    form = FilterForm(meta={'csrf': False})
    query = Income.query.order_by(desc(Income.created_at))

    if form.validate_on_submit():
        if form.start_date.data:
            query = query.filter(Income.created_at >= form.start_date.data)
        if form.end_date.data:
            query = query.filter(Income.created_at <= form.end_date.data)

    filtered_income = query.with_entities(func.sum(Income.amount)).scalar() or 0
    incomes = query.all()
    for inc in incomes:
        inc.created_at = convert_to_local(inc.created_at)

    return render_template('view_incomes.html', incomes=incomes, form=form, filtered_income=filtered_income)


@app.route('/view/expenses', methods=['GET', 'POST'])
def view_expenses():
    """
    View and filter all expenses by optional date range.
    """
    form = FilterForm(meta={'csrf': False})
    query = Expense.query.order_by(desc(Expense.created_at))

    if form.validate_on_submit():
        if form.start_date.data:
            query = query.filter(Expense.created_at >= form.start_date.data)
        if form.end_date.data:
            query = query.filter(Expense.created_at <= form.end_date.data)

    filtered_expense = query.with_entities(func.sum(Expense.amount)).scalar() or 0
    expenses = query.all()
    for exp in expenses:
        exp.created_at = convert_to_local(exp.created_at)

    return render_template('view_expenses.html', expenses=expenses, form=form, filtered_expense=filtered_expense)

@app.route('/breakdown')
def breakdown():
    """
    View all expenses in a pie chart by category
    """
    results = db.session.query(Expense.category,func.sum(Expense.amount).label('total_pennies')).group_by(Expense.category).all()

    # convert pennies -> pounds
    chart_data = [['Category', 'Amount (£)']] + [
      [cat, total_pennies / 100.0]
      for cat, total_pennies in results
    ]

    return render_template('breakdown.html',
                           data=json.dumps(chart_data))
if __name__ == '__main__':
    app.run(debug=True)