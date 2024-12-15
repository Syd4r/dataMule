import pytest
import conftest
from flask import url_for, current_app
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

def test_login_already_authenticated(test_client,login_user):
    response = test_client.get('/login',follow_redirects=True)
    assert response.status_code == 200
    assert b"test user" in response.data

def test_register_already_logged_in(test_client,login_user):
    response = test_client.get('/login',follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_user_existence(test_client): 
    '''give account info for an email that has not been registered'''
    response = test_client.post('/login',data={
        "email": "asdfasdfasdfasdfasdfasdfasdf@asdfasdfasdfadsfasdfasdfasdf.com",
        "password": "1234",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid email, if your account" in response.data

def test_setup_logged_in(test_client,login_user):
    response = test_client.get('/setup',follow_redirects=True)
    assert response.status_code == 200
    assert b"test user" in response.data

def test_bad_setup_token(test_client):
    #sending an invalid token
    response = test_client.post('/setup',data={"token":'0'},follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid or expired token" in response.data

def test_no_setup_token(test_client):
    response = test_client.post('/setup',follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid or expired token" in response.data

def test_bad_user_token(test_client):
    #sending a valid token for an invalid user
    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=3600)
    token = s.dumps({'user_id': "-1"}).decode('utf-8')
    response = test_client.post('/setup',data={"token":token},follow_redirects=True)
    assert response.status_code == 200
    assert b"or user does not exist" in response.data

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

def test_reset_password_already_auth(test_client,login_user):
    response = test_client.get('/reset_password',follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_reset_password_bad_user(test_client):

    response = test_client.post('/reset_password', 
                                data={
                                "email":"fjfjfjfjfjjdkdlslaoweqopweidsfjl@asdfjklaskdjfxcvnaierao.com" 
                                },
                                follow_redirects=True)
    assert response.status_code == 200
    assert b"Account not registered; click first-time login" in response.data


def test_reset_password_valid_user(test_client,new_session):
    user = User(first_name="test", last_name="user", email="testuser@test.com", user_type="user")
    user.set_password("securepassword")
    new_session.add(user)

    response = test_client.post('/reset_password', data={
                                "email":"testuser@test.com"
                                },follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Email sent to testuser@test.com" in response.data
    new_session.rollback()

def test_new_password_redirect(test_client,login_user):
    response = test_client.get('/new_password',follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_new_password_no_token(test_client):

    response = test_client.post('/new_password',data={},follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid or expired token"

def test_new_password_bad_user(test_client):
    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=3600)
    token = s.dumps({'user_id': "-1"}).decode('utf-8')
    response = test_client.post('/new_password',data={"token":token},follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid token or user does not exist" in response.data

def test_new_password_bad_token(test_client):
    #sending an invalid token
    response = test_client.post('/new_password',data={"token":'0'},follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid or expired token" in response.data

def test_new_password_valid_user(test_client,new_session):
    user = User(first_name="test123", last_name="user", email="testuser@test.com", user_type="user")
    user.set_password("securepassword")
    new_session.add(user)

    retrieved = new_session.query(User).filter_by(email="testuser@test.com").first()
    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=3600)
    token = s.dumps({'user_id':retrieved.id}).decode('utf-8')

    response = test_client.post('/new_password',data={
                'token':token,
                'password': "newPassword",
                },follow_redirects=True)

    new_session.rollback()
    new_session.delete(retrieved)
    new_session.commit()
    assert response.status_code == 200
    #assert b"Invalid or expired token" in response.data
    assert b"Welcome" in response.data #assume this reroutes to main

