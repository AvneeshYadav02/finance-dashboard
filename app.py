from data import TransactionManager

from flask import Flask, render_template, request, redirect, session, url_for, flash

tm = TransactionManager()
app = Flask(__name__)

app.secret_key = "super_secret_key_that_I_wont_tell_anyone"

@app.route("/")
def dashboard():
    role = session.get("role", "user")

    if (role == "admin"):
        return render_template(
            "admin/index.html",
            active_page="dashboard",
            role=role
        )
    else:
        # hardcoded user_id for sample usage
        user_id = 1
        user_stats = tm.getStats(user_id=user_id)
        transactions = tm.getTransactions(user_id=user_id)
        cat_breakdown = tm.catBreakdown(user_id=user_id)
        return render_template(
            "user/index.html",
            active_page="dashboard",
            role=role,
            user_stats = user_stats,
            transactions = transactions,
            cat_breakdown = cat_breakdown
        )

@app.route("/switch-role/<role>")
def switch_role(role):
    if role in ["user", "admin"]:
        session["role"]=role
        flash(role, "mode-switch")
    return redirect(url_for("dashboard"))

@app.route("/switch-theme/<theme>")
def switch_theme(theme):
    if theme in ["light", "dark"]:
        session["theme"]=theme
    return "", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)