from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DB_FILE = 'payroll.db'

# ✅ Initialize Database
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS employees (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        hourly_rate REAL)''')

        c.execute('''CREATE TABLE IF NOT EXISTS work_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employee_id INTEGER,
                        date TEXT,
                        hours REAL,
                        FOREIGN KEY(employee_id) REFERENCES employees(id))''')

        c.execute('''CREATE TABLE IF NOT EXISTS payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employee_id INTEGER,
                        date TEXT,
                        amount REAL,
                        FOREIGN KEY(employee_id) REFERENCES employees(id))''')
        conn.commit()

# ✅ Get database connection
def get_db():
    return sqlite3.connect(DB_FILE)

# ✅ Calculate balance for each employee
def calculate_balance(employee_id):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT hourly_rate FROM employees WHERE id=?", (employee_id,))
        rate = c.fetchone()[0]

        c.execute("SELECT SUM(hours) FROM work_logs WHERE employee_id=?", (employee_id,))
        total_hours = c.fetchone()[0] or 0

        c.execute("SELECT SUM(amount) FROM payments WHERE employee_id=?", (employee_id,))
        total_paid = c.fetchone()[0] or 0

    return (total_hours * rate) - total_paid

@app.route('/')
def index():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM employees")
        employees = c.fetchall()

        balances = []
        for emp in employees:
            emp_id, name, rate = emp
            balance = calculate_balance(emp_id)
            balances.append((emp_id, name, rate, balance))

    return render_template('index.html', balances=balances)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name']
    rate = float(request.form['rate'])

    with get_db() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO employees (name, hourly_rate) VALUES (?, ?)", (name, rate))
        conn.commit()

    return redirect(url_for('index'))

@app.route('/log_hours', methods=['POST'])
def log_hours():
    emp_id = int(request.form['employee_id'])
    date = request.form['date']
    hours = float(request.form['hours'])

    with get_db() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO work_logs (employee_id, date, hours) VALUES (?, ?, ?)", (emp_id, date, hours))
        conn.commit()

    return redirect(url_for('index'))

@app.route('/make_payment', methods=['POST'])
def make_payment():
    emp_id = int(request.form['employee_id'])
    date = request.form['date']
    amount = float(request.form['amount'])

    with get_db() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO payments (employee_id, date, amount) VALUES (?, ?, ?)", (emp_id, date, amount))
        conn.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
