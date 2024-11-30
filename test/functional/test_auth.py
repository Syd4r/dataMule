import pytest
import conftest
from flask import url_for
from werkzeug.security import generate_password_hash
from website.models import User
from website import db
from itsdangerous import TimedJSONWebSignatureSerializer

def test_login_success(test_client):
    """Test successful login."""
    response = test_client.post('/login', data={
        "email": "super@admin.com",
        "password": "password",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data  # Assuming the main.index page contains 'Welcome'

def test_login_failure(test_client):
    """Test login failure with wrong credentials."""
    response = test_client.post('/login', data={
        "email": "super@admin.com",
        "password": "wrongpassword",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data

def test_logout(test_client):
    """Test logout functionality."""
    test_client.post('/login', data={
        "email": "super@admin.com",
        "password": "password",  
    })
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data

def test_register_user_not_found(test_client):
    """Test registration when user does not exist in the database."""
    response = test_client.post('/register', data={
        "first_name": "Jane",
        "last_name": "Doe",
        "birth_date": "01/01/1990",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"User not found" in response.data

def test_register_send_email(test_client):
    """Test registration sends email when user exists."""

    response = test_client.post('/register', data={
        "first_name": "Jon",
        "last_name": "Mears",
        "birth_date": "04/30/2003",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Email sent" in response.data

def test_setup_password(test_client, secret_key):
    """Test password setup process."""

    user = User.query.filter_by(email="jon.mears@colby.edu").first()
    if user is None:
        user = User.query.filter_by(email='jgmear25@colby.edu').first()

    token = TimedJSONWebSignatureSerializer(secret_key, expires_in=3600).dumps({"user_id": user.id}).decode("utf-8")

    response = test_client.post('/setup', data={
        "email": "jgmear25@colby.edu",
        "password": "newpassword123",
        "token": token,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome, Jon Mears" in response.data

    # Verify password update
    user = User.query.filter_by(email='jgmear25@colby.edu').first()
    assert user is not None
    assert user.check_password("newpassword123")

def test_reset_password_page(test_client):
    """Test reset password page loads correctly."""
    response = test_client.get('/reset_password')
    assert response.status_code == 200
    assert b"Reset Password" in response.data
