from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import random
import string
from init_db import init_db  # ✅ import the db initializer

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.secret_key = 'your_secret_key'  # Change this to a secure key

# Function to generate a random CAPTCHA string
def generate_random_captcha(length=5):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

DATABASE = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def get_users():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")  # Removed email for users list
    users = cursor.fetchall()
    conn.close()
    return users

@app.route('/')
def home():
    username = session.get('username')
    if username:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user:
            return render_template('index.html', 
                                   username=user['username'],
                                   email=user.get('email', 'No email provided'),
                                   phone_number=user.get('phone_number', 'No phone number provided'),
                                   country=user.get('country', 'No country provided'),
                                   city=user.get('city', 'No city provided'),
                                   pincode=user.get('pincode', 'No pincode provided'))
    
    return render_template('index.html', username=None)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_captcha = request.form.get('captcha')
        session_captcha = session.get('captcha', '')

        if not user_captcha or user_captcha != session_captcha:
            flash("CAPTCHA validation failed. Please try again.", "danger")
            return redirect(url_for('signup'))

        # ✅ Get all form fields
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        country = request.form.get('country')
        city = request.form.get('city')
        pincode = request.form.get('pincode')

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO users (username, password, email, phone_number, country, city, pincode)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, email, phone_number, country, city, pincode))
            conn.commit()
            conn.close()

            flash("Sign Up successful! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already taken. Please choose a different one.", "danger")
            return redirect(url_for('signup'))

    # Generate a new CAPTCHA on GET request
    captcha = generate_random_captcha()
    session['captcha'] = captcha
    return render_template('signup.html', generatedCaptcha=captcha)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic here (check username/password)
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash("Login successful!", "success")
            return redirect(url_for('home'))  # Redirect to homepage or dashboard
        else:
            flash("Invalid credentials. Please try again.", "danger")
    
    return render_template('login.html')  # Ensure this template exists


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


# Initialize the database and run the app
if __name__ == '__main__':
    init_db()  # Initialize DB (if not already done)
    app.run(debug=True)
