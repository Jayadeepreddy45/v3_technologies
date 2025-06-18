from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv
load_dotenv()
from werkzeug.utils import secure_filename




app = Flask(__name__)
app.secret_key = 'your-super-secret-key'
CORS(app)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- SQLAlchemy Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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


    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "experience_years": self.experience_years,
            "technical_skills": self.technical_skills,
            "message": self.message
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

if __name__ == '__main__':
    app.run(debug=True)
