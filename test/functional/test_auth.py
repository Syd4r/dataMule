import pytest
from flask import url_for
from werkzeug.security import generate_password_hash
from website.models import User
from website import db
from itsdangerous import TimedJSONWebSignatureSerializer

def test_login_success(client):
    """Test successful login."""
    response = client.post(url_for('auth.login'), data={
        "email": "john.doe@colby.edu",
        "password": "password123",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data  # Assuming the main.index page contains 'Welcome'


def test_login_failure(client):
    """Test login failure with wrong credentials."""
    response = client.post(url_for('auth.login'), data={
        "email": "john.doe@colby.edu",
        "password": "wrongpassword",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_logout(client, app):
    """Test logout functionality."""
    with client:
        client.post(url_for('auth.login'), data={
            "email": "john.doe@colby.edu",
            "password": "password123",
        })
        response = client.get(url_for('auth.logout'), follow_redirects=True)
        assert response.status_code == 200
        assert b"Log In" in response.data  # Assuming the login page contains 'Log In'


def test_register_user_not_found(client):
    """Test registration when user does not exist in the database."""
    response = client.post(url_for('auth.register'), data={
        "first_name": "Jane",
        "last_name": "Doe",
        "birth_date": "1990-01-01",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"User not found" in response.data


def test_register_send_email(client, app):
    """Test registration sends email when user exists."""
    with app.app_context():
        user = User.query.filter_by(first_name="John", last_name="Doe").first()
        user.birth_date = "1990-01-01"
        db.session.commit()

    response = client.post(url_for('auth.register'), data={
        "first_name": "John",
        "last_name": "Doe",
        "birth_date": "1990-01-01",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Email sent" in response.data


def test_setup_password(client, app):
    """Test password setup process."""
    with app.app_context():
        user = User.query.filter_by(email="john.doe@colby.edu").first()
        s = app.config['SECRET_KEY']
        token = TimedJSONWebSignatureSerializer(s, expires_in=3600).dumps({"user_id": user.id}).decode("utf-8")

    response = client.post(url_for('auth.setup', token=token), data={
        "email": "new.email@colby.edu",
        "password": "newpassword123",
        "token": token,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Password set successfully" in response.data

    # Verify password update
    with app.app_context():
        user = User.query.filter_by(email="new.email@colby.edu").first()
        assert user is not None
        assert user.check_password("newpassword123")


def test_reset_password_page(client):
    """Test reset password page loads correctly."""
    response = client.get(url_for('auth.reset_password'))
    assert response.status_code == 200
    assert b"Reset Password" in response.data
