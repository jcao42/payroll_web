from flask import Flask, render_template, request, session
import csv
import io
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            num_employees = int(request.form['num_employees'])
            session['num_employees'] = num_employees
            return render_template('index.html', num_employees=num_employees, show_form=True)
        except:
            return render_template('index.html', show_form=False)
    return render_template('index.html', show_form=False)

@app.route('/results', methods=['POST'])
def results():
    employees = []
    num_employees = session.get('num_employees', 0)
    date = request.form.get('date', datetime.today().strftime('%Y-%m-%d'))

    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    filename = os.path.join(log_dir, f'payroll_log_{date}.csv')

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Name', 'Rate', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Total Hours', 'Total Pay'])

        for i in range(1, num_employees + 1):
            name = request.form.get(f'name_{i}', 'N/A')
            rate = float(request.form.get(f'rate_{i}', 0))
            hours = [float(request.form.get(f'{day}_{i}', 0)) for day in ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']]
            total_hours = sum(hours)
            total_pay = total_hours * rate

            writer.writerow([date, name, rate] + hours + [total_hours, total_pay])

            employees.append({
                'name': name,
                'rate': rate,
                'hours': hours,
                'total_hours': total_hours,
                'total_pay': total_pay
            })

    return render_template('results.html', employees=employees, date=date)

if __name__ == '__main__':
    app.run(debug=True)
