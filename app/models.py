from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    health_profile = db.relationship('HealthProfile', backref='user', uselist=False, cascade="all, delete-orphan")

class HealthProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    dietary_preferences = db.Column(db.String(200), nullable=True)
    allergies = db.Column(db.String(300), nullable=True)
    medical_conditions = db.Column(db.String(300), nullable=True)
    lifestyle_habits = db.Column(db.String(300), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
