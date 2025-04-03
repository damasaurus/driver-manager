from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import csv, os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
FAMILY_PASSWORD = "1234"

# Utility to read CSV safely
def read_csv(path):
    try:
        with open(path) as f:
            return list(csv.reader(f))
    except:
        return []

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        driver = request.form.get("driver")
        action = request.form.get("action")

        if action in ["Checkin", "Checkout"]:
            log_time(driver, action)

        elif action == "Upload":
            purpose = request.form.get("purpose")
            amount = request.form.get("amount")
            file = request.files["file"]
            if file:
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                save_expense(driver, purpose, amount, filename)

        return redirect("/")

    return render_template("index.html")

@app.route("/driver", methods=["GET", "POST"])
def driver_portal():
    if request.method == "POST":
        driver = request.form.get("driver")
        action = request.form.get("action")

        if action in ["Checkin", "Checkout"]:
            log_time(driver, action)

        elif action == "Upload":
            purpose = request.form.get("purpose")
            amount = request.form.get("amount")
            file = request.files["file"]
            if file:
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                save_expense(driver, purpose, amount, filename)

        return redirect("/driver")

    return render_template("driver.html")

@app.route("/family", methods=["GET", "POST"])
def family_portal():
    if request.method == "POST":
        password = request.form.get("password")
        if password == FAMILY_PASSWORD:
            return redirect(url_for("family_dashboard"))
        return render_template("family.html", error="Invalid password")
    return render_template("family.html", error=None)

@app.route("/family/dashboard")
def family_dashboard():
    logs = read_csv("data/logs.csv")
    expenses = read_csv("data/expenses.csv")
    salary = read_csv("data/salary.csv")

    salary_breakdown = {}
    for row in salary:
        if len(row) > 3:
            name = row[0]
            breakdown = row[3]
            salary_breakdown[name] = breakdown

    # Format dates
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)

    for row in logs:
        try:
            row[0] = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue

    for row in expenses:
        try:
            row[0] = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue

    return render_template("dashboard.html", logs=logs, expenses=expenses, salary=salary,
                           breakdowns=salary_breakdown,
                           today=today, yesterday=yesterday, week_ago=week_ago)

def log_time(driver, action):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("data/logs.csv", "a") as f:
        f.write(f"{now},{driver},{action}\n")

def save_expense(driver, purpose, amount, filename):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("data/expenses.csv", "a") as f:
        f.write(f"{now},{driver},{purpose},{amount},{filename}\n")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
