from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Athlete

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

@main_blueprint.route('/add_athletes', methods=['GET', 'POST'])
@login_required
def add_athletes():
    if request.method == 'POST':
        if 'action' in request.form:
            action = request.form.get('action')
            if action == 'add':
                hawkins_id = request.form.get('hawkins_id')
                first_name = request.form.get('first_name')
                last_name = request.form.get('last_name')
                birth_date = request.form.get('birth_date')
                gender = request.form.get('gender')
                sport = request.form.get('sport')
                position = request.form.get('position')
                grad_year = request.form.get('grad_year')

                athlete = Athlete(hawkins_id=hawkins_id, first_name=first_name, last_name=last_name, birth_date=birth_date, gender=gender, sport=sport, position=position, grad_year=grad_year)
                db.session.add(athlete)
                db.session.commit()


                flash('Athlete added successfully!', 'success')
                
            elif action == 'delete':

                flash('Athlete deleted successfully!', 'success')

    return render_template("add_athletes.html")


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