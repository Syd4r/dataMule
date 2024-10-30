from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Athlete
import os

# Create a blueprint
main_blueprint = Blueprint('main', __name__)


def get_links(user):
    links = [
        {
            "name": "Home",
            "url": url_for("main.index"),
            "icon": "NONE"
        }
    ]

    if user.user_type == "admin" or user.user_type == "super_admin":
        links += [
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
        links += [
            {
                "name": "Hawkins Dynamics",
                "url": url_for("main.hawkin"),
                "icon": "images/hawkin.jpg"
            }
        ]

    if user.user_type == "super_admin":
        links += [
            {
                "name": "View/Edit Admins",
                "url": url_for("main.add_admins"),
                "icon": "images/admins.png"
            }
        ]
    
    return links

# Routes
@main_blueprint.route('/', methods=['GET'])
@login_required
def index():
    user = current_user
    name = user.first_name + " " + user.last_name
    return render_template("index.html", user_name=name, links=get_links(user))

@main_blueprint.route('/hawkin', methods=['GET'])
@login_required
def hawkin():
    return render_template("hawkin.html", links=get_links(current_user))

@main_blueprint.route('/add_athletes', methods=['GET', 'POST'])
@login_required
def add_athletes():
    if request.method == 'POST' and 'action' in request.form:
        action = request.form.get('action')
        hawkins_id = request.form.get('hawkins_id')
        
        if hawkins_id:
            form_data = {
                'hawkins_id': hawkins_id,
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name'),
                'birth_date': request.form.get('birth_date'),
                'gender': request.form.get('gender'),
                'sport': request.form.get('sport'),
                'position': request.form.get('position'),
                'grad_year': request.form.get('grad_year')
            }
            athlete = Athlete.query.filter_by(hawkins_id=hawkins_id).first()
            try:
                if action == 'add' and not athlete:
                    db.session.add(Athlete(**form_data))
                    flash('Athlete added successfully!', 'success')
                elif action == 'delete' and athlete:
                    db.session.delete(athlete)
                    flash('Athlete deleted successfully!', 'success')
                db.session.commit()
            except Exception:
                flash(f"Error {action}ing athlete!", 'error')
        else:
            file = request.files.get('file')
            if not file or file.filename == '':
                flash('No file selected!', 'error')
            else:
                process_csv(file, action)
    
    return render_template("add_athletes.html", links=get_links(current_user))

def process_csv(file, action):
    try:
        file.save(file.filename)
        with open(file.filename, 'r') as f:
            lines = [line.split(',') for line in f.readlines()[1:]]
            for data in lines:
                if len(data) == 8:
                    data = [x.strip().replace('"', '').replace('\n', '') for x in data]
                    athlete = Athlete.query.filter_by(hawkins_id=data[0]).first()
                    if action == 'add' and athlete is None:
                        db.session.add(Athlete(*data))
                    elif action == 'delete' and athlete:
                        db.session.delete(athlete)
        db.session.commit()
        flash(f"Athletes {action}ed successfully!", 'success')
        os.remove(file.filename)
    except Exception as e:
        flash(f"Error {action}ing athletes!", 'error')
        print(e, data)



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