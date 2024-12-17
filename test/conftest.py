import pytest
from website import create_app, db
from website.models import User, Admin, SuperAdmin, Athlete, Coach, Team, TeamUserAssociation, AthletePerformance, Note
import os
from werkzeug.security import generate_password_hash
from flask_login import login_user

@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://eu7j42aanx9919j0:d3q831zu7dxey4bd@thh2lzgakldp794r.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/yog0wc5n980ulao5'
    with app.app_context():
        db.create_all()
        
    yield app
    with app.app_context():
        db.session.remove()

@pytest.fixture(scope='function')
def session(test_app):
    with test_app.app_context():
        yield db.session
        db.session.rollback()

@pytest.fixture()
def test_client():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://eu7j42aanx9919j0:d3q831zu7dxey4bd@thh2lzgakldp794r.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/yog0wc5n980ulao5'

    with flask_app.app_context():
        db.create_all()
        with flask_app.test_client() as test_client:
            yield test_client
    
    with flask_app.app_context():
        db.session.remove()

@pytest.fixture()
def new_session():
    yield db.session

@pytest.fixture()
def secret_key():
    flask_app = create_app()

    yield flask_app.config['SECRET_KEY']

@pytest.fixture()
def login_user(test_client,new_session):
    user = User(first_name="test", last_name="user", email="testuser@test.com", user_type="user")
    #if the user already exists, delete it
    existing_user = new_session.query(User).filter_by(email="testuser@test.com").first()
    if existing_user:
        new_session.delete(existing_user)
        new_session.commit()
    user.set_password("securepassword")
    new_session.add(user)
    new_session.commit()

    test_client.post('/login', data={
        "email": "testuser@test.com",
        "password": "securepassword",
    }, follow_redirects=True)
    yield
    new_session.delete(user)
    new_session.commit()

@pytest.fixture()
def login_athlete(test_client,new_session):
    athlete = Athlete(
        hawkins_id="H1234", first_name="Test", last_name="Athlete",
        birth_date="2000-01-01", gender="M", sport="Testing",
        position="Tester", grad_year=2024
    )
    existing_athlete = new_session.query(Athlete).filter_by(email="testathlete@test.com").first()
    if existing_athlete:
        new_session.delete(existing_athlete)
        new_session.commit()
    athlete.email = "testathlete@test.com"
    athlete.set_password("password")
    new_session.add(athlete)
    new_session.commit()

    test_client.post('/login', data={
        "email": "testathlete@test.com",
        "password": "password",
    }, follow_redirects=True)
    yield
    new_session.delete(athlete)
    new_session.commit()

@pytest.fixture()
def login_coach(test_client,new_session):
    football = new_session.query(Team).filter_by(name="Football").first()
    coach = Coach(
        team_id=football.id,
    )
    coach.first_name="Andy"
    coach.last_name="Nuggies Reid"
    coach.email = "coach@coach.com"
    coach.set_password("password")
    new_session.add(coach)
    new_session.commit()

    test_client.post('/login', data={
        "email": "coach@coach.com",
        "password": "password",
    }, follow_redirects=True)
    yield
    new_session.delete(coach)
    new_session.commit()

@pytest.fixture()
def login_SuperAdmin(test_client,new_session):
    user = SuperAdmin(first_name="test", last_name="user", email="testuser@test.com")
    existing_user = new_session.query(SuperAdmin).filter_by(email="testuser@test.com").first()
    if existing_user:
        new_session.delete(existing_user)
        new_session.commit()
    user.set_password("securepassword")
    new_session.add(user)
    new_session.commit()

    test_client.post('/login', data={
        "email": "testuser@test.com",
        "password": "securepassword",
    }, follow_redirects=True)

    yield

    new_session.delete(user)
    new_session.commit()