from flask import Flask, render_template, request, redirect, url_for
import csv, os
from datetime import datetime
import pytz

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

INDIA_TZ = pytz.timezone('Asia/Kolkata')
LOG_FILE = "data/logs.csv"
EXPENSE_FILE = "data/expenses.csv"
os.makedirs("data", exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def driver_portal():
    if request.method == "POST":
        driver = request.form.get("driver")
        action = request.form.get("action")

        if action in ["Checkin", "Checkout"]:
            log_time(driver, action)
        elif action == "Upload":
            # This won't be triggered here due to form separation
            pass

    return render_template("driver.html")

@app.route("/upload", methods=["POST"])
def upload():
    driver = request.form.get("driver")
    purpose = request.form.get("purpose")
    amount = request.form.get("amount")
    file = request.files["file"]

    if file:
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        save_expense(driver, purpose, amount, filename)

    return redirect(url_for("driver_portal"))

@app.route("/dashboard")
def dashboard():
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, newline="") as f:
            reader = csv.reader(f)
            logs = list(reader)
    return render_template("dashboard.html", logs=logs)

def log_time(driver, action):
    now = datetime.now(INDIA_TZ)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([now.isoformat(), driver, action])

def save_expense(driver, purpose, amount, filename):
    now = datetime.now(INDIA_TZ)
    with open(EXPENSE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([now.isoformat(), driver, purpose, amount, filename])

if __name__ == "__main__":
    app.run(debug=True)
