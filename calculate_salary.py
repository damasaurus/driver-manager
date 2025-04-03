import csv
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

# Settings
BASE_SALARY = 23000
OVERTIME_RATE = 70
DINNER_ALLOWANCE = 150
SUNDAY_RATE = 750
DINNER_TIME = datetime.strptime("21:30", "%H:%M").time()
WORK_START = datetime.strptime("09:30", "%H:%M").time()
WORK_END = datetime.strptime("19:30", "%H:%M").time()

PAID_LEAVE_DRIVERS = {"Sitaram"}

# Initialize data
driver_data = defaultdict(lambda: {
    "working_days": set(),
    "paid_leaves": 0,
    "unpaid_leaves": 0,
    "overtime_hours": 0,
    "dinner_days": 0,
    "sundays": 0,
    "travel_total": 0,
    "advance_total": 0
})

# Read check-in/check-out logs
with open("data/logs.csv", "r") as f:
    reader = csv.reader(f)
    logs = defaultdict(list)
    for row in reader:
        timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        driver = row[1]
        action = row[2]
        logs[(driver, timestamp.date())].append((timestamp, action))

# Calculate overtime and bonuses
for (driver, date), events in logs.items():
    checkin = next((t for t, a in events if a.lower() == "checkin"), None)
    checkout = next((t for t, a in events if a.lower() == "checkout"), None)
    if not checkin or not checkout:
        continue

    weekday = date.weekday()
    driver_data[driver]["working_days"].add(date)

    # Overtime before 9:30 AM
    if checkin.time() < WORK_START:
        overtime_morning = (datetime.combine(date, WORK_START) - checkin).total_seconds() / 3600
    else:
        overtime_morning = 0

    # Overtime after 7:30 PM
    if checkout.time() > WORK_END:
        overtime_evening = (checkout - datetime.combine(date, WORK_END)).total_seconds() / 3600
    else:
        overtime_evening = 0

    driver_data[driver]["overtime_hours"] += (overtime_morning + overtime_evening)

    # Dinner allowance
    if checkout.time() > DINNER_TIME:
        driver_data[driver]["dinner_days"] += 1

    # Sunday work
    if weekday == 6:
        driver_data[driver]["sundays"] += 1

# Read travel reimbursements
with open("data/expenses.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        driver = row[1]
        purpose = row[2].lower()
        amount = float(row[3])
        if purpose == "travel":
            driver_data[driver]["travel_total"] += amount

# Read advances (optional)
try:
    with open("data/advances.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            driver = row[1]
            amount = float(row[2])
            driver_data[driver]["advance_total"] += amount
except FileNotFoundError:
    pass

# Estimate leaves
all_dates = set()
for driver in driver_data:
    all_dates.update(driver_data[driver]["working_days"])
all_working_days = {d for d in all_dates if d.weekday() < 6}  # Monday-Saturday

for driver in driver_data:
    days_present = driver_data[driver]["working_days"]
    expected_days = {d for d in all_working_days if d.month == max(d.month for d in all_working_days)}
    absent_days = expected_days - days_present
    if driver in PAID_LEAVE_DRIVERS:
        driver_data[driver]["paid_leaves"] = len(absent_days)
    else:
        driver_data[driver]["unpaid_leaves"] = len(absent_days)

# Generate salary summary
with open("data/salary.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        "Driver", "Base Salary", "Paid Leaves", "Unpaid Leaves",
        "Overtime ₹", "Dinner ₹", "Sunday ₹", "Travel ₹", "Advance ₹", "Final Salary ₹"
    ])
    for driver, data in driver_data.items():
        overtime_pay = round(data["overtime_hours"] * OVERTIME_RATE)
        dinner_pay = data["dinner_days"] * DINNER_ALLOWANCE
        sunday_pay = data["sundays"] * SUNDAY_RATE
        unpaid_deduction = round((BASE_SALARY / 26) * data["unpaid_leaves"])
        final = BASE_SALARY + overtime_pay + dinner_pay + sunday_pay + data["travel_total"] - data["advance_total"] - unpaid_deduction
        writer.writerow([
            driver,
            BASE_SALARY,
            data["paid_leaves"],
            data["unpaid_leaves"],
            overtime_pay,
            dinner_pay,
            sunday_pay,
            data["travel_total"],
            data["advance_total"],
            round(final)
        ])

print("✅ Salary summary written to data/salary.csv")