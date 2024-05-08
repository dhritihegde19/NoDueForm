from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from forms import CreateRegisterForm, LoginForm
from functools import wraps
from flask import abort
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired
app = Flask(__name__)
app.config['SECRET_KEY'] = "secretkey"
ckeditor = CKEditor(app)
Bootstrap(app)

# Setting up the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from flask_migrate import Migrate

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Define User and Dues models
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

class Dues(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    university_seatnumber = db.Column(db.String(100), nullable=False)
    year_in_which_joined = db.Column(db.String(100), nullable=False)
    year_in_which_course_completed = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    reason_for_leaving = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text, nullable=False)
    mobile_number = db.Column(db.String(20), nullable=False)
    library_image = db.Column(db.String(100))
    hostel_image = db.Column(db.String(100))
    hod_image = db.Column(db.String(100))
    placement_office_image = db.Column(db.String(100))
    account_suptd_image = db.Column(db.String(100))
    academic_suptd_image = db.Column(db.String(100))


# Define the form for submitting dues
class DueForm(FlaskForm):
    student_name = StringField('Student Name', validators=[DataRequired()], render_kw={"style": "font-size:30px;text-align:center"})
    university_seatnumber = StringField('University Seat Number', validators=[DataRequired()], render_kw={"style": "font-size:30px;text-align:center"})
    year_in_which_joined = StringField('Year in which joined', validators=[DataRequired()], render_kw={"style": "font-size:30px;text-align:center"})
    year_in_which_course_completed = StringField('Year in which course is completed', validators=[DataRequired()], render_kw={"style": "font-size:30px;text-align:center"})
    department = SelectField('Department', choices=[('CSE', 'Computer Science Engineering'), ('ISE', 'Information Science Engineering'), ('CSE FULL STACK','Computer Science Full stack Engeering'),('AIML','Artificial intelligence and machine learning'),('AIDS','Artificial intelligence and Data science'),('AI and Robotics','Robotics and Artificial intelligence'),('Civil Engineering','Civil Engineering'),('Btech','Biotech Engineering'),('Mechanical Engineering','Mechanical Engineering'),('CNC','Computer science and communication Engineering'),('Cyber security','Cyber security Engeering'),('ENC','Electronis and COmmunication Engineering'),('Electronics VLSI','Electronics VLSI design Engineering'),('ENE','Electronics and Electrical Engineering')], validators=[DataRequired()], render_kw={"style": "font-size:30px"})
    reason_for_leaving = TextAreaField('Reason for leaving the college', validators=[DataRequired()], render_kw={"style": "font-size:30px;text-align:center"})
    address = TextAreaField('Address', validators=[DataRequired()], render_kw={"style": "font-size:30px"})
    mobile_number = StringField('Mobile Number', validators=[DataRequired()], render_kw={"style": "font-size:30px"})
    library_image = FileField('Library Image')
    hostel_image = FileField('Hostel Image')
    hod_image = FileField('HOD Image')
    placement_office_image = FileField('Placement Office Image')
    account_suptd_image = FileField('Account Suptd Image')
    academic_suptd_image = FileField('Academic Suptd Image')
    submit = SubmitField("Submit")
# Database creation
db.create_all()

# Admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes

@app.route('/')
def home():

    return render_template("index.html", current_user=current_user)

@app.route('/due_details/<int:id>')
def due_details(id):
    due = Dues.query.get_or_404(id)
    return render_template('due_details.html', due=due)

@app.route('/posts')
def get_all_posts():
    if current_user.is_authenticated and current_user.id == 1:
        dues = Dues.query.all()
        return render_template("index.html", current_user=current_user, dues=dues)
    return render_template("index.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    # Check if there are any existing users in the database
    existing_users = User.query.all()

    if not existing_users:  # If there are no existing users, the first registered user will be the admin
        is_admin = True
    else:
        is_admin = False

    # Handle registration form submission
    if request.method == "POST":
        form = CreateRegisterForm()
        if form.validate_on_submit():
            if not is_admin and not form.email.data.endswith("@nmamit.in"):
                flash("Registration is restricted to NMAMIT students.")
                return redirect(url_for('register'))

            user = User.query.filter_by(email=form.email.data).first()
            if not user:
                hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
                new_user = User(email=form.email.data, name=form.name.data, password=hashed_password)
                # Set admin status for the first registered user
                if is_admin:
                    new_user.is_admin = True
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for("login"))
            else:
                flash("This email already exists")
                return redirect(url_for('register'))
    else:
        form = CreateRegisterForm()

    return render_template("register.html", form=form)
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login'))
    return render_template("login.html", form=form)

@app.route('/submit_dues', methods=['GET', 'POST'])
def submit_dues():
    form = DueForm()
    if form.validate_on_submit():
        due = Dues(
            student_name=form.student_name.data,
            university_seatnumber=form.university_seatnumber.data,
            year_in_which_joined=form.year_in_which_joined.data,
            year_in_which_course_completed=form.year_in_which_course_completed.data,
            department=form.department.data,
            reason_for_leaving=form.reason_for_leaving.data,
            address=form.address.data,
            mobile_number=form.mobile_number.data,
            library_image=form.library_image.data.filename if form.library_image.data else None,
            hostel_image=form.hostel_image.data.filename if form.hostel_image.data else None,
            hod_image=form.hod_image.data.filename if form.hod_image.data else None,
            placement_office_image=form.placement_office_image.data.filename if form.placement_office_image.data else None,
            account_suptd_image=form.account_suptd_image.data.filename if form.account_suptd_image.data else None,
            academic_suptd_image=form.academic_suptd_image.data.filename if form.academic_suptd_image.data else None
        )
        db.session.add(due)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('submit_dues.html', form=form)

@app.route('/submit_success')
def submit_success():
    return 'Form submitted successfully!'

@app.route("/delete/<int:id>")
@admin_only
def delete_due(id):
    due_to_delete = Dues.query.get(id)
    db.session.delete(due_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
