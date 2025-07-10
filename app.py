from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///payroll.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    rate = db.Column(db.Float)
    hours = db.Column(db.Float)
    date = db.Column(db.String(10))

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    today = date.today().isoformat()
    entries = Entry.query.filter_by(date=today).all()

    if request.method == 'POST':
        # Clear existing entries for today
        Entry.query.filter_by(date=today).delete()

        for i in range(1, 11):  # Up to 10 rows
            name = request.form.get(f'name_{i}')
            rate = request.form.get(f'rate_{i}')
            hours = request.form.get(f'hours_{i}')
            if name and rate and hours:
                try:
                    entry = Entry(
                        name=name,
                        rate=float(rate),
                        hours=float(hours),
                        date=today
                    )
                    db.session.add(entry)
                except ValueError:
                    continue  # Ignore bad inputs

        db.session.commit()
        return redirect('/')

    if not entries:
        entries = [Entry(name='', rate=0.0, hours=0.0) for _ in range(5)]

    return render_template('index.html', entries=entries, today=today)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
