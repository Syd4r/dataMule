import pytest
from website import create_app, db
from website.models import User, Admin, Athlete, Coach, Team, TeamUserAssociation, AthletePerformance, Note
import os
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://eu7j42aanx9919j0:d3q831zu7dxey4bd@thh2lzgakldp794r.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/yog0wc5n980ulao5'
    with app.app_context():
        db.create_all()
        # Add a test user
        user = User(
            first_name="John",
            last_name="Doe",
            email="john.doe@colby.edu",
            user_type="athlete",
            password_hash=generate_password_hash("password123"),
        )
        db.session.add(user)
        db.session.commit()
    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(test_app):
    return test_app.test_client()

@pytest.fixture(scope='function')
def session(test_app):
    with test_app.app_context():
        yield db.session
        db.session.rollback()  # Undo any changes after each test
