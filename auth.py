from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import db, User
from flask_login import login_user, login_required, logout_user, current_user

# Create a blueprint
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect already logged-in users to the main page
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form['email']
        colby_id = request.form['colby_id']

        print(email, colby_id)
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_colby_id(colby_id):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))  # Redirect to the main index page
        else:
            flash('Invalid username or password.', 'error')
    return render_template("login.html")
