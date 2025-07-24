from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import inspect, text

app = Flask(__name__)

# Use Render's DATABASE_URL or local SQLite for testing
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///payroll.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------
# Database Models
# ----------------------
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False, default=0.0)
    total_owed = db.Column(db.Float, nullable=False, default=0.0)  # Added field
    amount_paid = db.Column(db.Float, nullable=False, default=0.0)  # Added field

class WorkLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    hours_worked = db.Column(db.Float, nullable=False)

# ----------------------
# Auto-Update Schema Logic
# ----------------------
def update_schema():
    inspector = inspect(db.engine)

    # Ensure tables exist
    db.create_all()

    # Check for missing columns in Employee table
    columns = [col['name'] for col in inspector.get_columns('employee')]

    if 'total_owed' not in columns:
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE employee ADD COLUMN total_owed FLOAT DEFAULT 0.0'))
            print("✅ Added total_owed column")

    if 'amount_paid' not in columns:
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE employee ADD COLUMN amount_paid FLOAT DEFAULT 0.0'))
            print("✅ Added amount_paid column")

# Run schema check at startup
with app.app_context():
    update_schema()

# ----------------------
# Routes
# ----------------------
@app.route('/')
def index():
    employees = Employee.query.all()
    return render_template('index.html', employees=employees)

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
    date = request.form['date']
    hours_worked = float(request.form['hours_worked'])

    work_log = WorkLog(employee_id=employee_id, date=date, hours_worked=hours_worked)
    db.session.add(work_log)

    # Update total owed
    employee = Employee.query.get(employee_id)
    employee.total_owed += hours_worked * employee.hourly_rate

    db.session.commit()
    return redirect(url_for('index'))

@app.route('/make_payment', methods=['POST'])
def make_payment():
    employee_id = int(request.form['employee_id'])
    amount = float(request.form['amount'])

    employee = Employee.query.get(employee_id)
    employee.amount_paid += amount
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
