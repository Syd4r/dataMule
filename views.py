from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

# Create a blueprint
main_blueprint = Blueprint('main', __name__)

# Routes
@main_blueprint.route('/', methods=['GET'])
@login_required
def index():
    user = current_user
    name = user.first_name + " " + user.last_name

    links = [
        {
            "name": "Hawkins Dynamics",
            "url": url_for("main.hawkin"),
            "icon": "images/hawkin.jpg"
        }
    ]
    return render_template("index.html", user_name=name, links=links)

@main_blueprint.route('/hawkin', methods=['GET'])
@login_required
def hawkin():
    return render_template("hawkin.html")
