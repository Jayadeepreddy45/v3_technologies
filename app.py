# app.py (cleaned and merged version)

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify,session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# --- App Init ---
app = Flask(__name__)
app.secret_key = 'your-super-secret-key'
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Database ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Models (minimal, extend in models.py) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='user')
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

# Add additional models: Contact, Application, Vendor, Timesheet, Invoice, InvoiceItem as needed

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # TEMPORARY ADMIN LOGIN
        if email == 'admin@com' and password == 'admin123':
            session['is_admin'] = True
            flash("Logged in as admin (dev mode)", "success")
            return redirect(url_for('admin_dashboard'))

        # Normal user login via database
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully", "success")
            return redirect(url_for('dashboard'))

        flash("Invalid credentials", "danger")

    return render_template('auth/login.html')
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        flash("Unauthorized access", "danger")
        return redirect(url_for('login'))
    return render_template('admin/admin_dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for('login'))




# @app.route('/admin/login')
# def admin_login():
#     return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for('register'))
        new_user = User(full_name=full_name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully.", "success")
        return redirect(url_for('login'))
    return render_template("auth/register.html")


@app.route('/services')
def services():
    return render_template('services_page.html')

@app.route('/clients')
def clients():
    return render_template('clients.html')
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        company = request.form.get('company')
        inquiry_type = request.form.get('inquiry_type')
        message = request.form.get('message')

        # new_contact = Contact(name=name, email=email, phone=phone, company=company,
        #                       inquiry_type=inquiry_type, message=message)
        # db.session.add(new_contact)
        # db.session.commit()
        flash("Your message has been sent successfully.", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/careers', methods=['GET', 'POST'])
def careers():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        # You can handle the form data here
    return render_template('careers_page.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# Add additional merged routes here (invoices, vendors, timesheets, etc.)
@app.route('/admin/vendors')
def vendor_list():
    vendors = Vendor.query.all()  # Assuming Vendor is your model
    return render_template('admin/vendor_list.html', vendors=vendors)
# --- Login manager ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/admin/invoices/create', methods=['GET', 'POST'])
def create_invoice():
    vendors = Vendor.query.all()  # Assuming you have a Vendor model

    if request.method == 'POST':
        vendor_id = request.form['vendor_id']
        invoice_date = request.form['invoice_date']
        items = request.form['items']
        total = request.form['total']

        # Save to DB (create and commit Invoice)
        # new_invoice = Invoice(...)
        # db.session.add(new_invoice)
        # db.session.commit()

        flash("Invoice created successfully", "success")
        return redirect(url_for('invoice_management'))

    return render_template('admin/invoice_creation.html', vendors=vendors)
@app.route('/admin/invoices')
def invoice_management():
    invoices = Invoice.query.all()  # Replace with actual Invoice model
    return render_template('admin/invoice_management.html', invoices=invoices)

@app.route('/admin/timesheets')
def admin_timesheets():
    timesheets = Timesheet.query.all()  # Ensure Timesheet model exists
    return render_template('admin/admin_timesheets.html', timesheets=timesheets)

# --- Run ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)