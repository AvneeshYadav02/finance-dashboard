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
        return render_template("admin/index.html", active_page="dashboard", role=role)
    else:
        # hardcoded user_id for sample usage
        user_id = 1
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
        return render_template("admin/log.html")
    else:
        user_id = 1
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
