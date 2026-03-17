import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    if request.method == "GET":
        symbol = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol", session["user_id"])

        shares = db.execute("""SELECT
                                symbol,
                                (SELECT COALESCE(SUM(amount_of_shares), 0) FROM transactions WHERE user_id = ? AND symbol = t.symbol)
                                -
                                (SELECT COALESCE(SUM(amount_of_shares_sold), 0) FROM sells WHERE user_id = ? AND symbol = t.symbol)
                                AS total_shares
                            FROM transactions AS t
                            WHERE user_id = ?
                            GROUP BY symbol""",
                            session["user_id"], session["user_id"], session["user_id"])

        current_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        avg_bought = db.execute("SELECT symbol, AVG(price) AS avg FROM transactions WHERE user_id = ? GROUP BY symbol", session["user_id"])
        current_price = []
        for item in symbol:
            current_price.append(lookup(item["symbol"]))
        total_value = []
        portfolio_value = 0
        for i in shares:
            for j in current_price:
                if i["symbol"] == j["symbol"]:
                    total_value.append({i["symbol"]: round(i["total_shares"] * j["price"], 2)})
                    portfolio_value += i["total_shares"] * j["price"]


        return render_template("index.html", symbol=symbol, shares=shares, current_price=current_price, total_value=total_value,
                               avg_bought=avg_bought, current_cash=current_cash, portfolio_value=portfolio_value)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        symbol = request.form.get("symbol")
        symbol_dict = lookup(symbol.upper())
        if not symbol:
            return apology("Please, insert a symbol!", 400)
        elif symbol_dict == None:
            return apology("Please, insert a valid symbol", 400)

        shares = request.form.get("shares")
        try:
            if int(shares) <= 0:
                return apology("Please, insert a valid amount of shares", 400)
        except ValueError:
            return apology("Please, insert a valid integer amount of shares", 400)

        stock_price = symbol_dict["price"]
        total_stock_price = int(shares) * stock_price
        cash_in_account = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        if cash_in_account < total_stock_price:
            return apology("Insufficient Funds!")
        else:
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash_in_account - total_stock_price, session["user_id"])
            db.execute("INSERT INTO transactions (user_id, amount_of_shares, price, total_price, symbol) VALUES (?, ?, ?, ?, ?)",
                       session["user_id"], int(shares), stock_price, total_stock_price, symbol.upper())

        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    if request.method == "GET":
        symbol = db.execute("""SELECT symbol, timestamp, DATE(timestamp) AS day, TIME(timestamp) AS time, transaction_type, price, amount_of_shares
                            FROM transactions
                            WHERE user_id = ?
                            UNION
                            SELECT symbol, timestamp, DATE(timestamp) AS day, TIME(timestamp) AS time, transaction_type, price, amount_of_shares_sold
                            FROM sells
                            WHERE user_id = ?
                            ORDER BY timestamp DESC""",
                            session["user_id"], session["user_id"])


    return render_template("history.html", symbol=symbol)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        symbol = request.form.get("symbol")
        symbol_dict = lookup(symbol.upper())
        if not symbol:
            return apology("Please, insert a symbol!", 400)
        elif symbol_dict == None:
            return apology("Please, insert a valid symbol", 400)
        else:
            return render_template("quoted.html", symbol_dict=symbol_dict)

    elif request.method == "GET":
        return render_template("quote.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return apology("Please, type a username", 400)
        elif len(db.execute("SELECT username FROM users WHERE username = ?", username)) != 0:
            return apology("Username already in use", 400)


        password = request.form.get("password")
        confimation = request.form.get("confirmation")
        if not password:
            return apology("Plase, type a password", 400)
        elif password != confimation:
            return apology("Password doesn't match with confirmation", 400)


        return db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password)) and render_template("login.html")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        list_stocks_owned = [i["symbol"] for i in db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol", session["user_id"])]
        if not symbol:
            return apology("Please, select a symbol", 400)
        elif symbol not in list_stocks_owned:
            return apology("Can't sell a stock you don't own", 400)

        symbol_dict = lookup(symbol.upper())
        stock_price = symbol_dict["price"]
        amount_of_shares = db.execute("""SELECT
                                      (SELECT COALESCE(SUM(amount_of_shares), 0)
                                      FROM transactions
                                      WHERE user_id = ? AND symbol = ?)
                                      -
                                      (SELECT COALESCE(SUM(amount_of_shares_sold), 0)
                                      FROM sells
                                      WHERE user_id = ? AND symbol = ?)
                                      AS total_shares""",
                                      session["user_id"], symbol, session["user_id"], symbol)

        if int(shares) < 0:
            return apology("Please, insert a valid positive number", 400)
        elif int(shares) > amount_of_shares[0]["total_shares"]:
            return apology("Invalid amount. Do not own enough shares", 400)

        total_stock_price = int(shares) * stock_price

        db.execute("INSERT INTO sells (user_id, amount_of_shares_sold, price, total_price, symbol) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], int(shares), stock_price, total_stock_price, symbol.upper())

        cash_in_account = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash_in_account + total_stock_price, session["user_id"])

        return redirect(url_for("index"))

    elif request.method == "GET":
        list_stocks_owned = [i["symbol"] for i in db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol", session["user_id"])]
        return render_template("sell.html", list_stocks_owned=list_stocks_owned)


@app.route("/funds", methods=["GET", "POST"])
@login_required
def funds():
    """This allows the user to add funds to his cash"""
    if request.method == "POST":
        amount = request.form.get("amount")
        confirmation = request.form.get("confirmation")
        if not amount or not confirmation:
            return apology("Please, insert an amount!", 400)
        elif float(amount) <= 0 or float(confirmation) <= 0:
            return apology("Please, insert a valid amount!", 400)
        elif float(amount) != float(confirmation):
            return apology("Values do not match!", 400)

        cash_in_account = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        db.execute("UPDATE users SET cash = ? WHERE id = ?", float(cash_in_account) + float(amount), session["user_id"])

        return redirect(url_for("index"))

    elif request.method == "GET":
        cash_in_account = round(db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"], 2)
        print(cash_in_account)
        return render_template("funds.html", cash_in_account=cash_in_account)

