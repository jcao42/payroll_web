import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# Secret Key for Session Management
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# Neon PostgreSQL Connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql://your_neon_connection_string'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# -------------------- MODELS --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    total_owed = db.Column(db.Float, default=0.0)
    amount_paid = db.Column(db.Float, default=0.0)

    @property
    def balance(self):
        return round(self.total_owed - self.amount_paid, 2)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    employee = db.relationship('Employee', backref=db.backref('payments', lazy=True))

# -------------------- AUTH --------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# -------------------- MAIN ROUTES --------------------
@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        return redirect(url_for('login'))

@app.route('/')
def index():
    employees = Employee.query.all()
    return render_template('index.html', employees=employees)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name']
    rate = float(request.form['hourly_rate'])
    employee = Employee(name=name, hourly_rate=rate)
    db.session.add(employee)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_hours', methods=['POST'])
def add_hours():
    employee_id = request.form['employee_id']
    hours = float(request.form['hours'])
    employee = Employee.query.get(employee_id)
    if employee:
        employee.total_owed += hours * employee.hourly_rate
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/record_payment', methods=['POST'])
def record_payment():
    employee_id = request.form['employee_id']
    amount = float(request.form['amount'])
    payment_date = request.form['date']
    payment = Payment(employee_id=employee_id, amount=amount, date=payment_date)
    employee = Employee.query.get(employee_id)
    if employee:
        employee.amount_paid += amount
        db.session.add(payment)
        db.session.commit()
    return redirect(url_for('index'))

# -------------------- INIT --------------------
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
