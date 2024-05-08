from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField

##WTForm


class NoDueForm(FlaskForm):
    student_name = StringField("Student Name", validators=[DataRequired()])
    university_seatnumber = StringField("University Seat Number", validators=[DataRequired()])
    yearinwhichjoined = StringField("Year in which joined", validators=[DataRequired()])
    yearinwhichcourseiscompleted = StringField("Year in which course is completed", validators=[DataRequired()])
    department = StringField("Department", validators=[DataRequired()])
    reason_for_leaving = TextAreaField("Reason for leaving the college", validators=[DataRequired()])
    address = TextAreaField("Address", validators=[DataRequired()])
    mobile_no = StringField("Mobile no.", validators=[DataRequired()])
    library = TextAreaField("Library", validators=[DataRequired()])
    hostel = TextAreaField("Hostel", validators=[DataRequired()])
    hod = TextAreaField("HOD", validators=[DataRequired()])
    placement_office = TextAreaField("Placement Office", validators=[DataRequired()])
    account_supdt = TextAreaField("Account Supdt", validators=[DataRequired()])
    academic_supdt = TextAreaField("Academic Supdt", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CreateRegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let me in!!")
