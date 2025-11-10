import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True, template_folder='../templates', static_folder='../static')

    # --- Configuration ---
    load_dotenv()
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')
    # Use SQLite and store it in the instance folder
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'site.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

    # Ensure the instance and upload folders exist
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Already exists
    try:
        os.makedirs(UPLOAD_FOLDER)
    except OSError:
        pass # Already exists

    # --- Initialize Extensions with App ---
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # --- Blueprints and Routes ---
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # --- Database Model Loading ---
    from . import models
    with app.app_context():
        db.create_all() # Create sql tables for our data models

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    return app
