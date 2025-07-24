from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///payroll.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Employee Model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    total_owed = db.Column(db.Float, default=0.0)
    amount_paid = db.Column(db.Float, default=0.0)

# Work Log Model
class WorkLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    hours = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    employees = Employee.query.all()
    logs = WorkLog.query.all()
    return render_template('index.html', employees=employees, logs=logs)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name']
    hourly_rate = float(request.form['hourly_rate'])
    new_employee = Employee(name=name, hourly_rate=hourly_rate)
    db.session.add(new_employee)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/log_hours', methods=['POST'])
def log_hours():
    employee_id = int(request.form['employee_id'])
    hours = float(request.form['hours'])
    employee = Employee.query.get(employee_id)

    if employee:
        owed_amount = hours * employee.hourly_rate
        employee.total_owed += owed_amount
        new_log = WorkLog(employee_id=employee_id, hours=hours)
        db.session.add(new_log)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/make_payment', methods=['POST'])
def make_payment():
    employee_id = int(request.form['employee_id'])
    amount = float(request.form['amount'])
    employee = Employee.query.get(employee_id)

    if employee:
        if amount > employee.total_owed:
            amount = employee.total_owed
        employee.total_owed -= amount
        employee.amount_paid += amount
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
