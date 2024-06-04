from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = 'loan_management1.db'

# Function to get database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Teardown function to close database connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Login route
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        # Handle login form submission
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if user:
            session['username'] = username
            flash('You were successfully logged in', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You were successfully logged out', 'success')
    return redirect(url_for('index'))

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

# Home route
@app.route('/home')
def home():
    if 'username' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('index'))
    return render_template('index.html')

# Manage loans route
@app.route('/manage_loans', methods=['GET', 'POST'])
def manage_loans():
    if 'username' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('index'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM loans")
    loans = cursor.fetchall()
    return render_template('manage_loans.html', loans=loans)

# Add loan route
@app.route('/add_loan', methods=['POST'])
def add_loan():
    if request.method == 'POST':
        amount = request.form['amount']
        customer = request.form['customer']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO loans (amount, customer) VALUES (?, ?)", (amount, customer))
        db.commit()
        flash('Loan added successfully', 'success')
        return redirect(url_for('manage_loans'))


# Delete loan route
@app.route('/delete_loan/<int:loan_id>', methods=['POST'])
def delete_loan(loan_id):
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM loans WHERE id = ?", (loan_id,))
        db.commit()
        flash('Loan deleted successfully', 'success')
        return redirect(url_for('manage_loans'))
    


# Manage users route
@app.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    if 'username' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('index'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    return render_template('manage_users.html', users=users)

# Add user route
@app.route('/add_user', methods=['POST'])
def add_user():
    if 'username' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('index'))
    
    username = request.form['username']
    password = request.form['password']
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    db.commit()
    
    flash('User added successfully', 'success')
    return redirect(url_for('manage_users'))

# Delete user route
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'username' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('index'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    
    flash('User deleted successfully', 'success')
    return redirect(url_for('manage_users'))

# Manage borrowers route
@app.route('/manage_borrowers', methods=['GET', 'POST'])
def manage_borrowers():
    if 'username' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('index'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM borrowers")
    borrowers = cursor.fetchall()
    
    return render_template('manage_borrowers.html', borrowers=borrowers)

# Add borrower route
@app.route('/add_borrower', methods=['POST'])
def add_borrower():
    if 'username' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('index'))
    
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']  # Get phone number from form
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO borrowers (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))  # Add phone to query
    db.commit()
    
    flash('Borrower added successfully', 'success')
    return redirect(url_for('manage_borrowers'))

# Delete borrower route
@app.route('/delete_borrower/<int:borrower_id>', methods=['POST'])
def delete_borrower(borrower_id):
    if 'username' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('index'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM borrowers WHERE id = ?", (borrower_id,))
    db.commit()
    
    flash('Borrower deleted successfully', 'success')
    return redirect(url_for('manage_borrowers'))


if __name__ == '__main__':
    app.run(debug=True)
