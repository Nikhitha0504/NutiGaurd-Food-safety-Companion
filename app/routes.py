from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
import os
from . import db, bcrypt
from .models import User, HealthProfile
from .forms import RegistrationForm, LoginForm, HealthProfileForm
from flask_login import login_user, current_user, logout_user, login_required
from .utils import extract_text_from_image, get_full_analysis_from_text, parse_json_response, allowed_file

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = HealthProfile.query.filter_by(user_id=current_user.id).first()
    form = HealthProfileForm(obj=profile)
    if form.validate_on_submit():
        if not profile:
            profile = HealthProfile(user_id=current_user.id)
            db.session.add(profile)
        form.populate_obj(profile)
        db.session.commit()
        flash('Your health profile has been updated!', 'success')
        return redirect(url_for('main.profile'))
    return render_template('profile.html', title='Health Profile', form=form)

@main.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        ocr_text = extract_text_from_image(filepath)
        if 'OCR Error' in ocr_text:
            return jsonify({'error': ocr_text}), 500
        
        profile = HealthProfile.query.filter_by(user_id=current_user.id).first()
        user_profile = None
        if profile:
            user_profile = {
                'name': profile.name,
                'age': profile.age,
                'gender': profile.gender,
                'height': profile.height,
                'weight': profile.weight,
                'dietary_preferences': profile.dietary_preferences,
                'allergies': profile.allergies,
                'medical_conditions': profile.medical_conditions,
                'lifestyle_habits': profile.lifestyle_habits,
            }

        analysis_text = get_full_analysis_from_text(ocr_text, user_profile)
        analysis_json = parse_json_response(analysis_text)

        if 'error' in analysis_json:
            return jsonify(analysis_json), 500

        # Add the image URL to the response
        analysis_json['image_url'] = url_for('static', filename=f'uploads/{filename}', _external=True)

        return jsonify(analysis_json)
    else:
        return jsonify({'error': 'Allowed file types are png, jpg, jpeg, gif, webp'}), 400

@main.route('/quick_analysis', methods=['POST'])
@login_required
def quick_analysis():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided for analysis'}), 400
    
    text = data['text']
    profile = HealthProfile.query.filter_by(user_id=current_user.id).first()
    user_profile = None
    if profile:
        user_profile = {
            'name': profile.name,
            'age': profile.age,
            'gender': profile.gender,
            'height': profile.height,
            'weight': profile.weight,
            'dietary_preferences': profile.dietary_preferences,
            'allergies': profile.allergies,
            'medical_conditions': profile.medical_conditions,
            'lifestyle_habits': profile.lifestyle_habits,
        }

    analysis_text = get_full_analysis_from_text(text, user_profile)
    analysis_json = parse_json_response(analysis_text)

    if 'error' in analysis_json:
        return jsonify(analysis_json), 500

    return jsonify(analysis_json)
