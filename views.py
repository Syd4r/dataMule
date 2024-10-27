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
    if user.user_type == "admin" or user.user_type == "super_admin":
        links = [
            {
                "name": "View/Edit Athletes",
                "url": url_for("main.add_athletes"),
                "icon": "images/athletes.png"
            },
            {
                "name": "View/Edit Coaches",
                "url": url_for("main.add_coaches"),
                "icon": "images/coaches.png"
            },
            {
                "name": "View/Edit Teams",
                "url": url_for("main.add_teams"),
                "icon": "images/teams.png"
            },
        ]
    else:
        links = [
            {
                "name": "Hawkins Dynamics",
                "url": url_for("main.hawkin"),
                "icon": "images/hawkin.jpg"
            }
        ]

    if user.user_type == "super_admin":
        links.append({
            "name": "View/Edit Admins",
            "url": url_for("main.add_admins"),
            "icon": "images/admins.png"
        })
    return render_template("index.html", user_name=name, links=links)

@main_blueprint.route('/hawkin', methods=['GET'])
@login_required
def hawkin():
    return render_template("hawkin.html")

@main_blueprint.route('/add_athletes', methods=['GET'])
@login_required
def add_athletes():
    pass

@main_blueprint.route('/add_coaches', methods=['GET'])
@login_required
def add_coaches():
    pass

@main_blueprint.route('/add_teams', methods=['GET'])
@login_required
def add_teams():
    pass

@main_blueprint.route('/add_admins', methods=['GET'])
@login_required
def add_admins():
    pass