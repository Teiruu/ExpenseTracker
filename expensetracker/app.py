from base import db
from flask import Flask, url_for, render_template
from model import Expense, AddExpense

app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)
with app.app_context():
    db.create_all()
    db.session.commit()


@app.route('/', methods=["GET"])
def expense_list():
    return render_template("index.html")

@app.route('/addexpense', methods=['POST'])
def add():
    form = AddExpense()
    if form.validate_on_submit():
        add_expense = Expense(
        category = form.category.data)
        add_expense.set_amount(form.amount.data)
        # Adding the task to the list
        db.session.add(add_expense)
        db.session.commit()
        return redirect(url_for('dashboard'))
