import csv
from io import StringIO
from data import TransactionManager
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
    flash,
    jsonify,
    Response,
    make_response,
)

tm = TransactionManager()
app = Flask(__name__)

app.secret_key = "super_secret_key_that_I_wont_tell_anyone"


@app.route("/")
def dashboard():
    role = session.get("role", "user")

    if role == "admin":
        sys_stats = tm.getFullStats()

        cat = sys_stats["categorical_volume"]
        cat_labels = list(cat.keys())
        cat_values = [val for val in cat.values()]

        user_logs = tm.getUserLogs()

        return render_template(
            "admin/index.html",
            active_page="dashboard",
            role=role,
            cat_labels=cat_labels,
            cat_values=cat_values,
            sys_stats=sys_stats,
            user_logs=user_logs,
        )
    else:
        # hardcoded user_id for sample usage
        user_id = 2
        if not tm.getUser(user_id):
            flash("Invalid user", "404")
        user_stats = tm.getStats(user_id=user_id)
        transactions = tm.getTransactions(user_id=user_id)

        breakdown = tm.catBreakdown(user_id=user_id)

        cat_breakdown = dict(
            sorted(breakdown.items(), key=lambda item: item[1], reverse=True)
        )

        cat_labels = list(cat_breakdown.keys())
        cat_values = [val for val in cat_breakdown.values()]
        return render_template(
            "user/index.html",
            active_page="dashboard",
            role=role,
            user_stats=user_stats,
            transactions=transactions,
            cat_breakdown=cat_breakdown,
            cat_labels=cat_labels,
            cat_values=cat_values,
        )


@app.route("/log")
def log():
    role = session.get("role", "user")

    if role == "admin":
        sys_stats = tm.getFullStats()

        user_logs = tm.getUserLogs()

        user_names = [user["name"] for user in user_logs]
        user_incomes = [user["income"] for user in user_logs]
        user_expenses = [user["expense"] for user in user_logs]

        return render_template(
            "admin/log.html",
            role=role,
            sys_stats=sys_stats,
            active_page="log",
            user_logs=user_logs,
            user_names=user_names,
            user_incomes=user_incomes,
            user_expenses=user_expenses,
        )
    else:
        user_id = 2
        if not tm.getUser(user_id):
            flash("Invalid user!", "404")
            return render_template(
                "user/log.html",
                active_page="log",
                user_id=user_id,
                role=role,
                user_stats={},
                transactions=[],
                transactions_count="--",
                last_transaction_date="--",
                cat_labels=[],
                cat_values=[],
            )

        user_stats = tm.getStats(user_id)
        transactions = tm.getTransactions(user_id)

        transactions_count = len(transactions)
        # last_transaction_date = None

        if transactions:
            last_transaction_date = max(
                t.get("date", "0000-00-00") for t in transactions
            )
        else:
            last_transaction_date = "No Transactions found"

        breakdown = tm.catBreakdown(user_id=user_id)

        cat_breakdown = dict(
            sorted(breakdown.items(), key=lambda item: item[1], reverse=True)
        )

        cat_labels = list(cat_breakdown.keys())
        cat_values = [val for val in cat_breakdown.values()]

        return render_template(
            "user/log.html",
            active_page="log",
            user_id=user_id,
            role=role,
            user_stats=user_stats,
            transactions=transactions,
            transactions_count=transactions_count,
            last_transaction_date=last_transaction_date,
            cat_labels=cat_labels,
            cat_values=cat_values,
        )


@app.route("/delete-user/<int:u_id>")
def delete_user(u_id):
    rm = tm.removeUser(u_id)
    return redirect(url_for("log"))


@app.route("/add-user", methods=["POST", "GET"])
def add_user():
    role = session.get("role")

    if request.method == "POST":
        user_name = request.form.get("name")
        user_balance = request.form.get("balance")

        if not (user_name or user_balance):
            flash("Please Fill All the Fields", "empty-fields")
            return render_template(
                "/admin/add_user.html", active_page="Add User", role=role
            )

        new_user = tm.addUser(user_name=user_name, user_balance=user_balance)

        return render_template(
            "admin/new_user.html",
            role=role,
            active_page=new_user["metadata"]["name"],
            user=new_user,
        )

    else:
        return render_template(
            "/admin/add_user.html", active_page="Add User", role=role
        )


@app.route("/add-transaction/<int:u_id>", methods=["POST", "GET"])
def add_transaction(u_id):
    role = session.get("role", "admin")

    user = tm.getUser(u_id)
    user_name = user["metadata"]["name"]
    user_currency = user["metadata"]["currency"]

    if request.method == "POST":
        t_amount = (request.form.get("amount"))
        t_category = (request.form.get("category")).title()
        t_type = (request.form.get("type")).lower()

        try:
            t_amount = int(t_amount)
        except ValueError:
            flash("Please Fill All the Fields", "empty-fields")
            return render_template(
                "/admin/add_transaction.html",
                user_id=u_id,
                user_currency=user_currency,
                active_page=user_name,
                role=role,
            )
        

        tm.addTransaction(
            user_id=u_id, tx_amount=t_amount, tx_category=t_category, tx_type=t_type
        )

        return redirect(f"/view-user/{u_id}")
    else:
        return render_template(
            "admin/add_transaction.html",
            role=role,
            user_id=u_id,
            user_currency=user_currency,
            active_page=user_name,
        )


@app.route("/view-user/<int:u_id>")
def view_user(u_id):
    user_id = u_id
    user = tm.getUser(user_id)
    user_name = user["metadata"]["name"]
    role = "admin"
    if not tm.getUser(user_id):
        flash("Invalid user!", "404")
        return render_template(
            "user/log.html",
            active_page=user_name,
            user_id=user_id,
            role=role,
            user_stats={},
            transactions=[],
            transactions_count="--",
            last_transaction_date="--",
            cat_labels=[],
            cat_values=[],
        )

    user_stats = tm.getStats(user_id)
    transactions = tm.getTransactions(user_id)

    transactions_count = len(transactions)
    # last_transaction_date = None

    if transactions:
        last_transaction_date = max(t.get("date", "0000-00-00") for t in transactions)
    else:
        last_transaction_date = "No Transactions found"

    breakdown = tm.catBreakdown(user_id=user_id)

    cat_breakdown = dict(
        sorted(breakdown.items(), key=lambda item: item[1], reverse=True)
    )

    cat_labels = list(cat_breakdown.keys())
    cat_values = [val for val in cat_breakdown.values()]

    return render_template(
        "admin/view_user.html",
        active_page=user_name,
        user_id=user_id,
        role=role,
        user_stats=user_stats,
        transactions=transactions,
        transactions_count=transactions_count,
        last_transaction_date=last_transaction_date,
        cat_labels=cat_labels,
        cat_values=cat_values,
    )


@app.route("/switch-role/<role>")
def switch_role(role):
    if role in ["user", "admin"]:
        session["role"] = role
        flash(role, "mode-switch")
    return redirect(url_for("dashboard"))


@app.route("/switch-theme/<theme>")
def switch_theme(theme):
    if theme in ["light", "dark"]:
        session["theme"] = theme
        session.modified = True
    return jsonify(success=True)


@app.route("/export-trans-logs/<user_id>")
def export_trans(user_id):
    transactions = tm.getTransactions(user_id)

    if not transactions:
        flash("No transactions to download", "404")
        return redirect(url_for("logs"))

    string_buffer = StringIO()
    cw = csv.writer(string_buffer)

    header = transactions[0].keys()
    cw.writerow(header)

    for t in transactions:
        cw.writerow(t.values())

    output = make_response(string_buffer.getvalue())
    output.headers["Content-Disposition"] = (
        f"attachment; filename=transaction_logs_{user_id}.csv"
    )
    output.headers["Content-Type"] = "text/csv"

    return output


if __name__ == "__main__":
    app.run(debug=True)
