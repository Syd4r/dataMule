import pytest
from flask import Flask
from flask_login import login_user
from website import db
from website.models import Athlete, Team, Coach, User
import os

@pytest.fixture
def test_user(app):
    with app.app_context():
        # Add a test user
        user = User(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            user_type="admin"
        )
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.rollback()


@pytest.fixture
def login_user(client, test_user):
    # Log in the test user for protected route testing
    with client.session_transaction() as session:
        login_user(test_user)


def test_index(client, login_user):
    # Test the index route
    response = client.get('/')
    assert response.status_code == 200
    assert b"Test User" in response.data  # Ensure user data is in the response


def test_hawkin_athlete_data(client, login_user, test_user):
    # Test /hawkin route for an athlete user
    test_user.user_type = "athlete"
    db.session.commit()

    response = client.get('/hawkin')
    assert response.status_code == 200
    assert b"athlete_data" in response.data


def test_hawkin_admin_data(client, login_user, test_user):
    # Test /hawkin route for an admin user
    test_user.user_type = "admin"
    db.session.commit()

    response = client.get('/hawkin')
    assert response.status_code == 200
    assert b"athlete_data" in response.data


def test_add_athletes(client, login_user):
    # Test adding an athlete
    response = client.post(
        '/add_athletes',
        data={
            'action': 'add',
            'hawkins_id': '12345',
            'first_name': 'John',
            'last_name': 'Doe',
            'birth_date': '2000-01-01',
            'gender': 'M',
            'sport': 'Football',
            'position': 'Quarterback',
            'grad_year': '2024',
        }
    )
    assert response.status_code == 200
    assert b"Athlete added successfully!" in response.data

    # Rollback the addition
    db.session.rollback()


def test_add_coaches(client, login_user):
    # Test adding a coach
    response = client.post(
        '/add_coaches',
        data={
            'action': 'add',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'team': 'Football'
        }
    )
    assert response.status_code == 200
    assert b"Coach added successfully!" in response.data

    # Rollback the addition
    db.session.rollback()

def test_add_teams(client, login_user):
    # Test adding a team
    response = client.post(
        '/add_teams',
        data={
            'action': 'add',
            'team_name': 'Football',
            'sport': 'Football'
        }
    )
    assert response.status_code == 200
    assert b"Team added successfully!" in response.data

    # Rollback the addition
    db.session.rollback()

def test_delete_athletes(client, login_user):
    # Test deleting an athlete
    # First, add an athlete to delete
    athlete = Athlete(
        hawkins_id='12345',
        first_name='John',
        last_name='Doe',
        birth_date='2000-01-01',
        gender='M',
        sport='Football',
        position='Quarterback',
        grad_year='2024'
    )
    db.session.add(athlete)
    db.session.commit()

    # Now delete the athlete
    response = client.post(
        '/delete_athletes',
        data={
            'action': 'delete',
            'hawkins_id': '12345'
        }
    )
    assert response.status_code == 200
    assert b"Athlete deleted successfully!" in response.data

    if athlete:
        db.session.delete(athlete)
        db.session.commit()

