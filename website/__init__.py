from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
import os
import pymysql
pymysql.install_as_MySQLdb()

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_default_secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace("postgres", "postgresql", 1)
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

    from .models import User
    from .views import main_blueprint
    from .auth import auth_blueprint

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Register blueprint for routes
    app.register_blueprint(main_blueprint)  
    app.register_blueprint(auth_blueprint)

    with app.app_context():
        db.create_all()  # This will create all tables defined in your models
        # app.run(debug=True, port=8080)

    return app