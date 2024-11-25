import pytest
from website import create_app, db
from website.models import User, Admin, SuperAdmin, Athlete, Coach, Team, TeamUserAssociation, AthletePerformance, Note
import os
from werkzeug.security import generate_password_hash
from flask_login import login_user

@pytest.fixture()
def test_client():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    with flask_app.app_context():
        with flask_app.test_client() as test_client:
            yield test_client

@pytest.fixture()
def secret_key():
    flask_app = create_app()

    yield flask_app.config['SECRET_KEY']

@pytest.fixture()
def athlete_user():
    user = Athlete.query.filter_by(first_name='Jon', last_name='Mears').first()
    login_user(user)

    yield user

@pytest.fixture()
def admin_user():
    admin = Admin.query.filter_by(first_name='Admin', last_name='Andy').first()
    login_user(admin)

    yield admin

@pytest.fixture()
def superadmin_user():
    superadmin = SuperAdmin.query.filter_by(first_name='Super', last_name='Admin').first()

    login_user(superadmin)
    yield superadmin
