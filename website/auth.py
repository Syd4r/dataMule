'''Functions for user authentication'''
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from website import db
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message

from website.email_utils import send_email  # Import send_email from the new email_utils
from itsdangerous import TimedJSONWebSignatureSerializer , BadSignature, SignatureExpired

# Create a blueprint
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    '''Function to log in a user'''
    # Redirect already logged-in users to the main page
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user is None:
            flash(f'''Invalid email, if your account hasn't 
                  been set up yet, click "First-Time Login"''', "error")
            return redirect(url_for('auth.login'))

        if check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('main.index'))

        flash("Invalid email or password", "error")
        return redirect(url_for('auth.login'))

    return render_template("login.html")

@auth_blueprint.route('/logout')
def logout():
    '''Function to log out a user'''
    logout_user()
    return redirect(url_for('auth.login'))

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    '''Function to register a user'''
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birth_date = request.form['birth_date']

        user = User.query.filter_by(first_name=first_name, last_name=last_name).first()
        if user is None:
            flash("User not found, please contact administrator if issue persists", "error")
            return redirect(url_for('auth.register'))
        
        email = f"{user.first_name.lower()}.{user.last_name.lower()}@colby.edu"

        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=3600)
        token = s.dumps({'user_id': user.id}).decode('utf-8')

        reset_link = url_for('auth.setup', token=token, _external=True)
        email_body = f'''
To set your email and password, visit the following link:
{reset_link}
'''

        # Send the email
        send_email("Set Your Password", email, email_body)

        flash(f"Email sent to {email} with link to set password", "success")
        return redirect(url_for('auth.register'))  # Redirect or render a different template

    return render_template("register.html")

@auth_blueprint.route('/setup', methods=['GET', 'POST'])
def setup():
    '''Function to set up a user's password'''
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    token = request.args.get('token') if request.method == 'GET' else request.form.get('token')
    if not token:
        flash("Invalid or expired token", "error")
        return redirect(url_for('auth.register'))

    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
        user_id = data.get('user_id')

        # Query the user from the database
        user = User.query.get(user_id)
        if user is None:
            flash("Invalid token or user does not exist", "error")
            return redirect(url_for('auth.register'))

    except (BadSignature, SignatureExpired):
        flash("Invalid or expired token", "error")
        return redirect(url_for('auth.register'))

    # If POST request, process form data to set up the password
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Update the user with the new password and email
        user.email = email
        user.password_hash = generate_password_hash(password)
        db.session.commit()

        flash("Password set successfully! You can now log in.", "success")
        login_user(user)
        return redirect(url_for('main.index'))

    # Render the setup form with the token (hidden field) for POST requests
    return render_template("setup.html", token=token)

@auth_blueprint.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    '''Function to reset a user's password'''
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form['email']

        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("Account not registered; click first-time login", "error")
            return redirect(url_for('auth.reset_password'))
        
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=3600)
        token = s.dumps({'user_id': user.id}).decode('utf-8')

        reset_link = url_for('auth.new_password', token=token, _external=True)
        email_body = f'''
To reset your email and password, visit the following link:
{reset_link}
'''
        # Send the email
        send_email("Reset Your Password", email, email_body)

        flash(f"Email sent to {email} with link to reset password", "success")
        return redirect(url_for('auth.reset_password'))  # Redirect or render a different template

    return render_template("reset_password.html")

@auth_blueprint.route('/new_password', methods=['GET', 'POST'])
def new_password():
    '''Function to set a new password'''
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    token = request.args.get('token') if request.method == 'GET' else request.form.get('token')
    if not token:
        flash("Invalid or expired token", "error")
        return redirect(url_for('auth.reset_password'))

    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
        user_id = data.get('user_id')

        # Query the user from the database
        user = User.query.get(user_id)
        if user is None:
            flash("Invalid token or user does not exist", "error")
            return redirect(url_for('auth.reset_password'))

    except (BadSignature, SignatureExpired):
        flash("Invalid or expired token", "error")
        return redirect(url_for('auth.reset_password'))

    # If POST request, process form data to set up the password
    if request.method == 'POST':
        password = request.form['password']

        # Update the user with the new password and email
        user.password_hash = generate_password_hash(password)
        db.session.commit()

        flash("Password set successfully! You can now log in.", "success")
        login_user(user)
        return redirect(url_for('main.index'))

    # Render the setup form with the token (hidden field) for POST requests
    return render_template("new_password.html", token=token)