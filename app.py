from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import csv, os, json
import pytz
from pywebpush import webpush, WebPushException

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# VAPID Keys (replace these with your actual keys)
VAPID_PUBLIC_KEY = "BBjr14hDEc4Gk2hZKnttyy8tLXjC8Kbpk558Gj4kpbX_s5L1w-pXkCWDigQIsmTvggDcK0e8zJ6JtV7EQnQ="
VAPID_PRIVATE_KEY = "LSoTLS1CRdJTiBQUKLWQRFIfEtWS0tLS0tCk1JRoBAhUR0J5cUdTTTQ5QWdFR0NbCudTTTQ5QXdFSEJHMHhd0lCQVFR2Z5STWp5OUtCVU9wWmMzNXAKZTFmTHhaeE9kNGx2Mm1jbExjUzNCYytvcnZlaFJBTkNBQVFZMFNZUE0UkhPQnBHWkdaN2JiY29mTDdTMTR3ZwpaS1N1ZWZCbytKWUd3MEY4VXYrCBQUklWQVRFIEtFWS0tLS0tCg=="
VAPID_CLAIMS = {"sub": "smeetmehta02@gmail.com"}

def send_push(title, message):
    try:
        with open("data/subscription.json", "r") as f:
            subscription_info = json.load(f)
        webpush(
            subscription_info=subscription_info,
            data=json.dumps({"title": title, "body": message}),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
        print("✅ Notification sent")
    except Exception as e:
        print("❌ Push failed:", e)

# Ensure data folders exist
os.makedirs("data", exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

INDIA_TZ = pytz.timezone('Asia/Kolkata')
LOG_FILE = "data/logs.csv"
EXPENSE_FILE = "data/expenses.csv"

@app.route("/", methods=["GET", "POST"])
def driver_portal():
    if request.method == "POST":
        driver = request.form.get("driver")
        action = request.form.get("action")

        if action in ["Checkin", "Checkout"]:
            log_time(driver, action)
            send_push("Driver Update", f"{driver} just {action.lower()}ed.")

        elif action == "Upload":
            purpose = request.form.get("purpose")
            amount = request.form.get("amount")
            file = request.files["file"]
            if file:
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                save_expense(driver, purpose, amount, filename)
                send_push("Reimbursement Uploaded", f"{driver} uploaded a bill for {purpose}.")

        return redirect(url_for("driver_portal"))
    return render_template("driver.html")

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

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/subscribe", methods=["POST"])
def subscribe():
    subscription = request.get_json()
    with open("data/subscription.json", "w") as f:
        json.dump(subscription, f)
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
