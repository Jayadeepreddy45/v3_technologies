from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
from vendor.app import create_vendor_app, db as vendor_db, blueprints as vendor_blueprints


load_dotenv()

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app)
app = create_vendor_app()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-super-secret-key'

# --- DB Setup ---
db = vendor_db  # ✅ Use the existing instance
migrate = Migrate(app, db)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Import & Register Vendor Blueprints ---
from vendor.app.routes.invoices import bp as invoices_bp
from vendor.app.routes.timesheets import bp as timesheets_bp
# add other vendor routes here...

app.register_blueprint(invoices_bp, url_prefix='/vendor', name='invoices_bp')

app.register_blueprint(timesheets_bp, url_prefix='/timesheets', name='timesheets_bp')


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    inquiry_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    current_position = db.Column(db.String(100))
    current_company = db.Column(db.String(100))
    experience_years = db.Column(db.String(20))
    work_description = db.Column(db.Text)
    education = db.Column(db.String(100))
    field_of_study = db.Column(db.String(100))
    institution = db.Column(db.String(100))
    graduation_year = db.Column(db.String(10))
    technical_skills = db.Column(db.Text)
    soft_skills = db.Column(db.Text)
    certifications = db.Column(db.Text)
    resume_filename = db.Column(db.String(255))
    cover_letter_filename = db.Column(db.String(255))
    availability = db.Column(db.String(50))
    salary_expectation = db.Column(db.String(100))
    work_location = db.Column(db.String(50))
    additional_info = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "experience_years": self.experience_years,
            "technical_skills": self.technical_skills,
            "education": self.education,
            "city": self.city,
            "state": self.state,
            "resume_filename": self.resume_filename
        }


@app.route('/submit_application', methods=['POST'])
def submit_application():
    form = request.form
    files = request.files

    # Save files
    resume_file = files.get('resume')
    cover_letter_file = files.get('coverLetter')

    resume_filename = None
    cover_letter_filename = None

    if resume_file:
        resume_filename = secure_filename(resume_file.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
        resume_file.save(resume_path)

    if cover_letter_file:
        cover_letter_filename = secure_filename(cover_letter_file.filename)
        cover_letter_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_letter_filename)
        cover_letter_file.save(cover_letter_path)

    new_app = Application(
        first_name=form.get('firstName'),
        last_name=form.get('lastName'),
        email=form.get('email'),
        phone=form.get('phone'),
        address=form.get('address'),
        city=form.get('city'),
        state=form.get('state'),
        zip_code=form.get('zipCode'),
        current_position=form.get('currentPosition'),
        current_company=form.get('currentCompany'),
        experience_years=form.get('experienceYears'),
        work_description=form.get('workDescription'),
        education=form.get('education'),
        field_of_study=form.get('fieldOfStudy'),
        institution=form.get('institution'),
        graduation_year=form.get('graduationYear'),
        technical_skills=form.get('technicalSkills'),
        soft_skills=form.get('softSkills'),
        certifications=form.get('certifications'),
        resume_filename=resume_filename,
        cover_letter_filename=cover_letter_filename,
        availability=form.get('availability'),
        salary_expectation=form.get('salaryExpectation'),
        work_location=form.get('workLocation'),
        additional_info=form.get('additionalInfo')
    )

    db.session.add(new_app)
    db.session.commit()

    return redirect(url_for('apply'))



@app.route('/get_applications', methods=['GET'])
def get_applications():
    apps = Application.query.all()
    return jsonify([app.to_dict() for app in apps])

@app.route('/init_db')
def init_db():
    db.create_all()
    return "Database initialized!"



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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Simple validation
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.")
            return redirect(url_for('register'))

        new_user = User(full_name=full_name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully. Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/apply')
def apply():
    return render_template('job_application_form.html')


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
    print("✅ submit_contact route triggered")
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    company = request.form.get('company')
    inquiry_type = request.form.get('inquiryType')
    message = request.form.get('message')

    if not (name and email and inquiry_type and message):
        flash("Please fill in all required fields.")
        return redirect(url_for('contact_page'))

    # Save to database
    contact = Contact(
        name=name,
        email=email,
        phone=phone,
        company=company,
        inquiry_type=inquiry_type,
        message=message
    )
    db.session.add(contact)
    db.session.commit()
    


    flash("Thank you! Your message has been saved.")
    return redirect(url_for('contact_page'))



@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/api/applications', methods=['GET'])
def api_applications():
    applications = Application.query.order_by(Application.created_at.desc()).all()
    return jsonify([
        {
            'id': app.id,
            'applicant': f"{app.first_name} {app.last_name}",
            'email': app.email,
            'phone': app.phone,
            'position': app.current_position or "",
            'status': app.status,
            'experience': app.experience_years,
            'education': app.education,
            'skills': app.technical_skills,
            'location': f"{app.city}, {app.state}",
            'availability': app.availability,
            'salary': app.salary_expectation,
            'resume': app.resume_filename,
            'appliedDate': app.created_at.strftime("%Y-%m-%d")
        }
        for app in applications
    ])

@app.route('/api/application/<int:app_id>/status', methods=['POST'])
def update_application_status(app_id):
    status = request.form.get('status')
    application = Application.query.get_or_404(app_id)
    application.status = status
    db.session.commit()
    return jsonify({"message": f"Status updated to {status}"})

# # Initialize vendor logic inside this app
# vendor_app = create_vendor_app()
# app.register_blueprint(vendor_app.blueprints[0], url_prefix='/vendor')  # Register each blueprint manually
# app.register_blueprint(vendor_app.blueprints[1], url_prefix='/vendor')
# app.register_blueprint(vendor_app.blueprints[2], url_prefix='/vendor')
# app.register_blueprint(vendor_app.blueprints[3], url_prefix='/vendor')
# app.register_blueprint(vendor_app.blueprints[4], url_prefix='/vendor')

for bp in vendor_blueprints:
    app.register_blueprint(bp, url_prefix='/vendor')

# Connect DB/migrations if needed
vendor_db.init_app(app)
Migrate(app, vendor_db)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
