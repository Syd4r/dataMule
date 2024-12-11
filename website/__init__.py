'''Initializes the app and sets up the database and mail server'''
import os
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
import pymysql
from dotenv import load_dotenv
from .models import User
from .views import main_blueprint
from .auth import auth_blueprint

load_dotenv()
pymysql.install_as_MySQLdb()

db = SQLAlchemy()

def create_app():
    '''Function to create the app'''
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_default_secret')
    database = os.getenv('DATABASE_URL').replace("postgres", "postgresql", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,  # Set your desired pool size here
        'max_overflow': 5,  # Optional
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'datamulecolby@gmail.com')

    mail = Mail(app)
    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        '''Function to load a user'''
        return User.query.get(int(user_id))

    # Register blueprint for routes
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    with app.app_context():
        db.create_all()  # This will create all tables defined in your models

    return app
