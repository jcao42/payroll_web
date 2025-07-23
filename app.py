import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'secretkey')

# Connect to Neon PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Employee model with balance tracking
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    total_hours = db.Column(db.Float, default=0)
    amount_owed = db.Column(db.Float, default=0)  # Outstanding balance

# Initialize DB (only first time)
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    employees = Employee.query.all()
    return render_template('index.html', employees=employees)

@app.route('/add_hours', methods=['POST'])
def add_hours():
    emp_id = request.form.get('id')
    hours = float(request.form.get('hours'))
    emp = Employee.query.get(emp_id)
    emp.total_hours += hours
    emp.amount_owed += hours * emp.hourly_rate
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/pay', methods=['POST'])
def pay():
    emp_id = request.form.get('id')
    amount = float(request.form.get('amount'))
    emp = Employee.query.get(emp_id)
    emp.amount_owed -= amount
    if emp.amount_owed < 0:
        emp.amount_owed = 0
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == os.environ.get('APP_USERNAME') and password == os.environ.get('APP_PASSWORD'):
            session['user'] = username
            return redirect(url_for('index'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
