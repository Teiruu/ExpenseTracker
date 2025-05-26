from base import db
from flask import Flask, url_for, render_template, redirect, request
from model import Expense, AddExpense

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
    return render_template("index.html", expenses=expenses)

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
    return render_template("add.html", form=form)

@app.route('/edit/<int:expense_id>', methods=["GET", "POST"])
def edit_expense(expense_id):
    expense = db.get_or_404(Expense, expense_id)

    if request.method == "POST":
        expense.category = request.form["category"]
        expense.set_amount(float(request.form["amount"]))  # ← convert input string to float
        db.session.commit()
        return redirect(url_for("expense_list"))

    return render_template("edit.html", expense=expense)

@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    # remove expense by ID
    expense = db.get_or_404(Expense, expense_id)

    if request.method == "POST":
        db.session.delete(expense)
        db.session.commit()
        return redirect(url_for("expense_list"))

    return render_template("index.html", expense=expense)