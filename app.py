from flask import Flask, render_template, request, redirect, session, url_for
import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")  # Use env variable in production

# Hardcoded credentials (move to env vars for security)
USERNAME = os.environ.get("APP_USERNAME", "admin")
PASSWORD = os.environ.get("APP_PASSWORD", "mypassword")

# Temporary in-memory payroll storage (could be replaced with DB)
payroll_data = {}

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Main payroll page
@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    today = datetime.date.today()
    if request.method == 'POST':
        name = request.form.get('name')
        hours = float(request.form.get('hours', 0))
        rate = float(request.form.get('rate', 0))

        if name:
            if name not in payroll_data:
                payroll_data[name] = {'total_hours': 0, 'rate': rate, 'owed': 0}
            payroll_data[name]['total_hours'] += hours
            payroll_data[name]['owed'] += hours * rate

    return render_template('index.html', payroll=payroll_data, today=today)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
