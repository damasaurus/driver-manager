from flask import Flask, render_template, request, redirect, url_for
import os
import csv
from datetime import datetime, timedelta
import pytz
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === Utility ===
def get_ist_now():
    return datetime.now(pytz.timezone('Asia/Kolkata'))

# === Ensure CSV files exist ===
for filename in ['logs.csv', 'expenses.csv', 'salary.csv']:
    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            if filename == 'logs.csv':
                writer.writerow(['Timestamp', 'Driver', 'Action'])
            elif filename == 'expenses.csv':
                writer.writerow(['Timestamp', 'Driver', 'Purpose', 'Amount', 'Filename'])
            elif filename == 'salary.csv':
                writer.writerow(['Driver', 'Month', 'Net Pay'])

# === ROUTES ===

@app.route('/')
def driver():
    return render_template('driver.html')

@app.route('/dashboard')
def dashboard():
    logs = []
    expenses = []
    breakdowns = {}
    salary = []

    # Load logs
    try:
        with open('logs.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                time = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
                logs.append((time, row[1], row[2]))
    except:
        logs = []

    # Load expenses
    try:
        with open('expenses.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                time = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
                expenses.append((time, row[1], row[2], row[3], row[4]))
    except:
        expenses = []

    # Load salary
    try:
        with open('salary.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                salary.append(row)
    except:
        salary = []

    # Fake breakdowns for now
    for row in salary:
        if row[0] != 'Driver':
            breakdowns[row[0]] = f"{row[0]} Salary for {row[1]}: ₹{row[2]} (detailed breakdown coming soon)"

    week_ago = datetime.now() - timedelta(days=7)
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    return render_template(
        'dashboard.html',
        logs=logs,
        expenses=expenses,
        salary=salary,
        breakdowns=breakdowns,
        week_ago=week_ago.date(),
        today=today,
        yesterday=yesterday
    )

@app.route('/driver', methods=['POST'])
def log_time():
    driver = request.form['driver']
    action = request.form['action']  # checkin or checkout
    now = get_ist_now()

    with open('logs.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([now, driver, action.capitalize()])

    return redirect(url_for('driver'))

@app.route('/upload', methods=['POST'])
def upload_expense():
    driver = request.form['driver']
    purpose = request.form['purpose']
    amount = request.form['amount']
    file = request.files['file']
    now = get_ist_now()

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        with open('expenses.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([now, driver, purpose, amount, filename])

        return redirect(url_for('driver'))

    return "Upload failed", 400

# === Run ===
if __name__ == '__main__':
    app.run(debug=True)
