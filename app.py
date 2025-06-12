from flask import Flask, render_template, request, redirect, url_for, flash
from flask_cors import CORS
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services_page.html')

@app.route('/clients')
def clients():
    return render_template('clients.html')

@app.route('/login')
def login():
    return render_template('login_page.html')

@app.route('/careers', methods=['GET', 'POST'])
def careers():

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        # Process data here
    return render_template('careers_page.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        message = request.form.get('message')
        # Process data here
    return render_template('contact_us_page.html')
@app.route('/contact_us_page.html')
def contact_page():
    return render_template('contact_us_page.html')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Here you can: save to a DB, send an email, log to a file, etc.
    print(f"Contact form submitted by {name} ({email}): {message}")

    flash("Thank you for reaching out! We'll get back to you soon.")
    return redirect(url_for('contact_page'))

if __name__ == '__main__':
    app.run(debug=True)
