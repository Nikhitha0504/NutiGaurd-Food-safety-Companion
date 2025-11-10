from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from .models import User

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class HealthProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    height = FloatField('Height (in cm)', validators=[DataRequired()])
    weight = FloatField('Weight (in kg)', validators=[DataRequired()])
    dietary_preferences = StringField('Dietary Preferences (e.g., vegetarian, vegan)')
    allergies = TextAreaField('Known Allergies (comma-separated)')
    medical_conditions = TextAreaField('Medical Conditions (comma-separated)')
    lifestyle_habits = TextAreaField('Lifestyle Habits (e.g., activity level, sleep hours)')
    submit = SubmitField('Save Profile')
