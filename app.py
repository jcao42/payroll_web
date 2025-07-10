from flask import Flask, render_template, request, redirect
from datetime import date
from models import db, Employee, Entry

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables on startup
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    today = date.today()

    if request.method == 'POST':
        for emp in Employee.query.all():
            hours_str = request.form.get(f"hours_{emp.id}", "")
            if hours_str.strip() != "":
                try:
                    hours = float(hours_str)
                    if hours >= 0:
                        entry = Entry(employee_id=emp.id, date=today, hours=hours)
                        db.session.add(entry)
                except ValueError:
                    pass  # Ignore invalid input
        db.session.commit()
        return redirect('/')

    employees = Employee.query.all()

    # Get today's hours
    entries = Entry.query.filter_by(date=today).all()
    entry_map = {e.employee_id: e.hours for e in entries}

    return render_template("index.html", employees=employees, entry_map=entry_map, today=today)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
