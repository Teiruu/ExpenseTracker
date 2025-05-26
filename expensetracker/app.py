from base import db
from flask import Flask, url_for, render_template, redirect, request
from model import Expense, AddExpense, AddIncome, Income

app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)
app.config.from_pyfile('instance/config.py')
with app.app_context():
    db.create_all()
    db.session.commit()


@app.route('/', methods=["GET"])
def expense_list():
    expenses = db.session.execute(db.select(Expense).order_by(Expense.expense_id)).scalars()
    incomes = db.session.execute(db.select(Income).order_by(Income.income_id)).scalars()
    return render_template("index.html", expenses=expenses, incomes=incomes)

@app.route('/add_expense', methods=["GET", "POST"])
def add_expense():
    form = AddExpense()
    if form.validate_on_submit():
        create_expense = Expense(
        category = form.category.data)
        create_expense.set_amount(form.amount.data)
        # Adding the task to the list
        db.session.add(create_expense)
        db.session.commit()
        return redirect(url_for('expense_list'))
    return render_template("add_expense.html", form=form)

@app.route('/edit/<int:expense_id>', methods=["GET", "POST"])
def edit_expense(expense_id):
    expense = db.get_or_404(Expense, expense_id)

    if request.method == "POST":
        expense.category = request.form["category"]
        expense.set_amount(float(request.form["amount"]))  # ← convert input string to float
        db.session.commit()
        return redirect(url_for("expense_list"))

    return render_template("edit_expense.html", expense=expense)

@app.route('/delete/<int:expense_id>', methods=['POST'])
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
        create_income = Income()
        create_income.set_amount(form.amount.data)
        # Adding the task to the list
        db.session.add(create_income)
        db.session.commit()
        return redirect(url_for('expense_list'))
    return render_template("add_income.html", form=form)