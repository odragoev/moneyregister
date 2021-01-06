import os
import datetime
from decimal import Decimal

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory, jsonify, json
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, cad

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


class Transaction():
    def __init__(self, ID, date, category, payee, description, deposit, payment, balance):
        self.ID = ID
        self.date = date
        self.category = category
        self.payee = payee
        self.description = description
        self.deposit = deposit
        self.payment = payment
        self.balance = balance


class Transac():
    def __init__(self, date, catkey, payee, description, deposit, payment):
        self.date = date
        self.catkey = catkey
        self.payee = payee
        self.description = description
        self.deposit = deposit
        self.payment = payment


# Taken from flask documentation for favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """ Home page """
    if request.method == "POST":
        # Add transaction clicked
        if "add_transaction" in request.form:
            return redirect("/add_transaction")

        # Edit transaction clicked
        if "edit_transaction" in request.form:
            # Get value of radio button clicked
            ID = request.form["IDs"]

            # Get information currently in user selected row
            query = "SELECT date, catkey, payee, description, deposit, payment "
            query += "FROM register "
            query += "WHERE id = :id"
            rows = db.execute(query, id=ID)
            date = rows[0]["date"]
            catkey = rows[0]["catkey"]
            payee = rows[0]["payee"]
            description = rows[0]["description"]
            dep = rows[0]["deposit"]
            pay = rows[0]["payment"]

            # Validate payment or deposit
            if pay == "":
                payment = ""
                deposit = Decimal(dep)
            else:
                payment = Decimal(pay)
                deposit = ""

            transaction = Transac(date, catkey, payee, description, deposit, payment)
            # Get categories to display in dropdown
            rows = db.execute("SELECT id, name FROM categories WHERE userkey = :userkey",
                              userkey=session["user_id"])

            categories = []
            for row in rows:
                categories.append((row["id"], row["name"]))

            return render_template(
                "edit_transaction.html", ID=ID, transaction=transaction, categories=categories)

        # Remove transaction clicked
        if "remove_transaction" in request.form:
            # Get value of radio button clicked
            ID = request.form["IDs"]
            db.execute("DELETE FROM register WHERE id = :id", id=ID)

            return redirect("/")
    else:
        # Get information to display in table
        query = ""
        query += "SELECT register.id, date, name, payee, description, deposit, payment "
        query += "FROM register INNER JOIN categories "
        query += "ON register.catkey = categories.id "
        query += "WHERE register.userkey = :userkey "
        query += "ORDER BY date(date)"
        rows = db.execute(query, userkey=session["user_id"])

        transactions = []

        for row in rows:
            ID = row["id"]
            date = row["date"]
            category = row["name"]
            payee = row["payee"]
            description = row["description"]
            dep = row["deposit"]
            pay = row["payment"]
            bal = 0

            # Display payment and deposit as CAD
            if pay != "":
                payment = cad(pay)
                deposit = ""
            if dep != "":
                payment = ""
                deposit = cad(dep)

            # Populate transactions array
            transaction = Transaction(ID, date, category, payee, description, deposit, payment, bal)
            transactions.append(transaction)

        # Calculate the user's balance
        balance = Decimal(0.00)
        for transaction in transactions:
            if transaction.deposit != "":
                balance += Decimal(transaction.deposit)
            if transaction.payment != "":
                balance -= Decimal(transaction.payment)
            transaction.balance = balance

        return render_template("index.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Get JSON data for username and password
        data = request.get_json()

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=data["username"])

        # Remember which user has logged in
        if len(rows) == 1:
            session["user_id"] = rows[0]["id"]

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], data["password"]):
            return '{"valid": "false"}'
        else:
            return '{"valid": "true"}'
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Hash password
        hash = generate_password_hash(request.form.get("password"))

        # Insert the user into the database
        primaryKey = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                                username=request.form.get("username"), hash=hash)
        session["user_id"] = primaryKey

        return redirect("/")
    else:
        # Query database for all usernames
        rows = db.execute("SELECT username FROM users")
        usernames = []
        for row in rows:
            usernames.append(row["username"])

        # Delimit usernames with | and send to form
        pipeDelimited = "|".join(usernames)
        return render_template("register.html", pipeDelimited=pipeDelimited)


@app.route("/add_transaction", methods=["GET", "POST"])
@login_required
def add_transaction():
    """Add a transaction"""
    if request.method == "POST":
        # Get information from the form
        date = request.form.get("date")
        catkey = request.form.get("category")
        payee = request.form.get("payee")
        description = request.form.get("description")
        deposit = request.form.get("deposit")
        payment = request.form.get("payment")

        # Insert row except for balance into the table
        query = ""
        query += "INSERT INTO register (userkey, catkey, date, payee, description, deposit, payment) "
        query += "VALUES(:userkey, :catkey, :date, :payee, :description, :deposit, :payment)"
        db.execute(query, userkey=session["user_id"],
                   catkey=catkey, date=date, payee=payee,
                   description=description, deposit=deposit,
                   payment=payment)

        return redirect("/")
    else:
        # Query for id and name of all categories
        rows = db.execute("SELECT id, name FROM categories WHERE userkey = :userkey",
                          userkey=session["user_id"])

        # Get categories to display in dropdown
        categories = []
        for row in rows:
            categories.append((row["id"], row["name"]))
        return render_template("add_transaction.html", categories=categories)


@app.route("/edit_transaction", methods=["GET", "POST"])
@login_required
def edit_transaction():
    """Edit a transaction"""
    if request.method == "POST":
        # Get information from the form
        date = request.form.get("date")
        catkey = request.form.get("category")
        payee = request.form.get("payee")
        description = request.form.get("description")
        deposit = request.form.get("deposit")
        payment = request.form.get("payment")
        ID = request.form.get("id")

        # Update information in chosen row
        query = ""
        query += "UPDATE register SET date=:date, catkey=:catkey, payee=:payee, "
        query += "description=:description, deposit=:deposit, payment=:payment "
        query += "WHERE id = :id"
        db.execute(query, date=date, catkey=catkey, payee=payee,
                   description=description, payment=payment, deposit=deposit, id=ID)

        return redirect("/")
    else:
        return redirect("/")


@app.route("/category", methods=["GET", "POST"])
@login_required
def category():
    """Home for categories"""
    if request.method == "POST":
        # Add category clicked
        if "add_category" in request.form:
            return redirect("/add_category")

        # Edit category clicked
        if "edit_category" in request.form:
            # Get value of radio button clicked
            ID = request.form["IDs"]

            # Get category name currently in user selected row
            rows = db.execute("SELECT name FROM categories WHERE id = :id", id=ID)

            return render_template("edit_category.html", ID=ID, name=rows[0]["name"])
    else:
        # Get categories to display in dropdown
        query = ""
        query += "SELECT id, name FROM categories "
        query += "WHERE userkey = :userkey"
        rows = db.execute(query, userkey=session["user_id"])

        # Get category id and name currently in user selected row
        categories = []
        for row in rows:
            categories.append((row["id"], row["name"]))

        return render_template("category.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
@login_required
def add_category():
    """Add a category"""
    if request.method == "POST":
        # Get category from form
        name = request.form.get("category")

        # Insert new category into table
        query = ""
        query += "INSERT INTO categories (userkey, name) "
        query += "VALUES (:userkey, :name)"
        db.execute(query, userkey=session["user_id"], name=name)

        return redirect("/category")
    else:
        # Query for name of all categories
        query = ""
        query += "SELECT name FROM categories "
        query += "WHERE userkey = :userkey"
        rows = db.execute(query, userkey=session["user_id"])
        categories = []
        for row in rows:
            categories.append(row["name"])

        # Delimit usernames with | and send to form
        pipeDelimited = "|".join(categories)

        return render_template("add_category.html", pipeDelimited=pipeDelimited)


@app.route("/edit_category", methods=["GET", "POST"])
@login_required
def edit_category():
    """Edit a transaction"""
    if request.method == "POST":
        # Get value of radio button clicked
        ID = request.form.get("id")

        # Get new category name from the form and update the table
        newCategory = request.form.get("category")
        query = ""
        query += "UPDATE categories SET name = :name "
        query += "WHERE id = :id"
        db.execute(query, name=newCategory, id=ID)

        return redirect("/category")
    else:
        return redirect("/category")