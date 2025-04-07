from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import os, csv

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
FAMILY_PASSWORD = "1234"

# ---- Utility: Safe CSV Reader ----
def read_csv(filepath):
    try:
        with open(filepath, newline='') as f:
            return list(csv.reader(f))
    except FileNotFoundError:
        return []

# ---- Logger Functions ----
def log_time(driver, action):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("data/logs.csv", "a") as f:
        f.write(f"{now},{driver},{action}\n")

def save_expense(driver, purpose, amount, filename):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("data/expenses.csv", "a") as f:
        f.write(f"{now},{driver},{purpose},{amount},{filename}\n")

# ---- Index Route (/): Unified Portal ----
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        driver = request.form.get("driver")
        action = request.form.get("action")

        if action in ["Checkin", "Checkout"]:
            log_time(driver, action)

        elif action == "Upload":
            purpose = request.form.get("purpose")
            amount = request.form.get("amount")
            file = request.files.get("file")
            if file:
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                save_expense(driver, purpose, amount, filename)

        return redirect("/")

    return render_template("index.html")

# ---- Driver Portal (alias route for redundancy) ----
@app.route("/driver", methods=["GET", "POST"])
def driver_portal():
    return redirect("/")

# ---- Family Login ----
@app.route("/family", methods=["GET", "POST"])
def family_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == FAMILY_PASSWORD:
            return redirect(url_for("family_dashboard"))
        return render_template("family.html", error="Invalid password.")
    return render_template("family.html", error=None)

# ---- Dashboard ----
@app.route("/family/dashboard")
def family_dashboard():
    logs = read_csv("data/logs.csv")
    expenses = read_csv("data/expenses.csv")
    salary = read_csv("data/salary.csv")

    # Convert timestamps in logs and expenses
    parsed_logs = []
    for row in logs:
        try:
            row[0] = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            parsed_logs.append(row)
        except Exception:
            continue

    parsed_expenses = []
    for row in expenses:
        try:
            row[0] = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            parsed_expenses.append(row)
        except Exception:
            continue

    # Parse salary breakdowns
    breakdowns = {}
    for row in salary:
        if len(row) > 3:
            breakdowns[row[0]] = row[3]

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)

    return render_template("dashboard.html",
                           logs=parsed_logs,
                           expenses=parsed_expenses,
                           salary=salary,
                           breakdowns=breakdowns,
                           today=today,
                           yesterday=yesterday,
                           week_ago=week_ago)

# ---- Run App ----
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
