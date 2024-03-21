from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
from datetime import date
import time

from util.main import *

app = Flask(__name__)
app.config['DATABASE'] = 'expenses.db'



def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    purpose TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date TEXT NOT NULL
                )''')
    db.commit()
    return render_template('index.html')

@app.route('/submit', methods=['POST','GET'])
def submit_expense():
    if request.method == 'POST':
        purpose = request.form['purpose']
        amount = float(request.form['amount'])
        date = request.form['date']
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''INSERT INTO expenses (purpose, amount, date) VALUES (?, ?, ?)''',
                       (purpose, amount, date))
        db.commit()
        time.sleep(2)
        return redirect(url_for('submit_expense', added=True))
    return render_template('index.html', added=request.args.get('added'))

@app.route('/expenses')
def view_expenses():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''SELECT sum(amount) FROM expenses''')
    total = cursor.fetchone()[0]
    total = format_indian_currency(total)
    
    cursor.execute('''SELECT * FROM expenses order by date desc''')
    expenses = cursor.fetchall()
    return render_template('expenses.html', expenses=expenses,total = total,display = False)    

@app.route('/filter_expenses', methods=['POST'])
def filter_expenses():
    selected_date = request.form['date']
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''SELECT SUM(amount) FROM expenses WHERE date = ?''',(selected_date,))
    total = cursor.fetchone()[0]
    total = format_indian_currency(total)

    cursor.execute('''SELECT * FROM expenses WHERE date = ?''',(selected_date,))
    expenses = cursor.fetchall()
    
    return render_template('expenses.html', expenses=expenses,total = total,date = selected_date,display = True)

@app.route('/delete_expense', methods=['POST'])
def delete_expense():
    expense_id = request.form['expense_id']
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''DELETE FROM expenses WHERE id = ?''', (expense_id,))
    db.commit()
    return redirect(url_for('view_expenses'))

@app.route('/report')
def report():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT SUM(amount) AS total_amount_week
        FROM expenses
        WHERE strftime('%Y-%m-%d', date) BETWEEN date('now', 'weekday 0', '-6 days') AND date('now', 'weekday 0')
    """)    
    total_amount_week = format_indian_currency(cursor.fetchone()[0])


    cursor.execute("""
        SELECT SUM(amount) AS total_amount_month
        FROM expenses
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', date('now'))
    """)
    total_amount_month = format_indian_currency(cursor.fetchone()[0])


    cursor.execute("""
        SELECT SUM(amount) AS total_amount_today
        FROM expenses
        WHERE date(date) = date('now')
    """)
    total_amount_today = format_indian_currency(cursor.fetchone()[0])

    cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
    """)
    total_amount = format_indian_currency(cursor.fetchone()[0])
    

    return render_template('report.html',
                           today = total_amount_today,
                           week = total_amount_week,
                           month = total_amount_month,
                           total = total_amount
                           )


