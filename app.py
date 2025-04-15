from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta, timezone
import os
import csv

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
LOG_FILE = 'data/logs.csv'
EXPENSE_FILE = 'data/expenses.csv'
SALARY_FILE = 'data/salary.csv'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
INDIA_TZ = timezone(timedelta(hours=5, minutes=30))

# Ensure upload and data folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def driver_portal():
    if request.method == "POST":
        driver = request.form.get("driver")
        action = request.form.get("action")

        if action in ["checkin", "checkout"]:
            log_time(driver, action.capitalize())

        return redirect(url_for("driver_portal"))

    return render_template("driver.html")

@app.route('/upload', methods=['POST'])
def upload_expense():
    from werkzeug.utils import secure_filename
    import pytz

    driver = request.form['driver']
    purpose = request.form['purpose']
    amount = request.form['amount']
    file = request.files['file']

    if file:
        # Save file to static/uploads/
        filename = secure_filename(file.filename)
        upload_path = os.path.join('static/uploads', filename)
        file.save(upload_path)

        # Get current time in IST
        india_time = datetime.now(pytz.timezone('Asia/Kolkata'))

        # Append to expenses.csv
        with open('expenses.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([india_time, driver, purpose, amount, filename])

        return redirect(url_for('driver'))

    return "Upload failed", 400

@app.route("/family/dashboard")
def family_dashboard():
    logs, expenses = [], []

    try:
        with open(LOG_FILE, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    dt = datetime.fromisoformat(row[0]).astimezone(INDIA_TZ)
                    logs.append([dt, row[1], row[2]])
                except:
                    continue
    except FileNotFoundError:
        pass

    try:
        with open(EXPENSE_FILE, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    dt = datetime.fromisoformat(row[0]).astimezone(INDIA_TZ)
                    expenses.append([dt, row[1], row[2], row[3], row[4]])
                except:
                    continue
    except FileNotFoundError:
        pass

    salary, breakdowns = [], {}
    try:
        with open(SALARY_FILE, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0] != "Driver":
                    salary.append(row)
                    breakdowns[row[0]] = row[3]
    except FileNotFoundError:
        pass

    today = datetime.now(INDIA_TZ).date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)

    return render_template("dashboard.html", logs=logs, expenses=expenses, salary=salary, breakdowns=breakdowns, today=today, yesterday=yesterday, week_ago=week_ago)

# ---- Run App ----
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
