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
    if request.method == 'POST':
        if 'action' in request.form:
            action = request.form.get('action')
            if action == 'add':
                if request.form.get('hawkins_id') is not None:
                    hawkins_id = request.form.get('hawkins_id')
                    first_name = request.form.get('first_name')
                    last_name = request.form.get('last_name')
                    birth_date = request.form.get('birth_date')
                    gender = request.form.get('gender')
                    sport = request.form.get('sport')
                    position = request.form.get('position')
                    grad_year = request.form.get('grad_year')

                    try:
                        athlete = Athlete(hawkins_id=hawkins_id, first_name=first_name, last_name=last_name, birth_date=birth_date, gender=gender, sport=sport, position=position, grad_year=grad_year)
                        db.session.add(athlete)
                        db.session.commit()
                        flash('Athlete added successfully!', 'success')
                    except Exception as e:
                        flash('Error adding athlete!', 'error')
                else:
                    file = request.files['file']
                    if file.filename == '':
                        flash('No file selected!', 'error')
                        return render_template("add_athletes.html", links=get_links(current_user))
                    try:
                        file.save(file.filename)
                        with open(file.filename, 'r') as f:
                            lines = f.readlines()
                            # Skip the first line
                            lines = lines[1:]
                            for line in lines:
                                data = line.split(',')
                                if len(data) == 8:
                                    #check if athlete already exists
                                    #trim and remove quoatation marks
                                    data = [x.strip().replace('"', '').replace('\n','') for x in data]
                                    athlete = Athlete.query.filter_by(hawkins_id=data[0], first_name=data[1], last_name=data[2], birth_date=data[3], gender=data[4], sport=data[5], position=data[6], grad_year=data[7]).first()
                                    if athlete is None:
                                        athlete = Athlete(hawkins_id=data[0], first_name=data[1], last_name=data[2], birth_date=data[3], gender=data[4], sport=data[5], position=data[6], grad_year=data[7])
                                        db.session.add(athlete)
                            db.session.commit()
                            flash('Athletes added successfully!', 'success')
                        # Delete the file
                        file.close()
                        os.remove(file.filename)
                    except Exception as e:
                        print(e)
                        print(data)
                        flash('Error adding athletes!', 'error')                
            elif action == 'delete':
                if request.form.get('hawkins_id') is not None:
                    hawkins_id = request.form.get('hawkins_id')
                    first_name = request.form.get('first_name')
                    last_name = request.form.get('last_name')
                    birth_date = request.form.get('birth_date')
                    gender = request.form.get('gender')
                    sport = request.form.get('sport')
                    position = request.form.get('position')
                    grad_year = request.form.get('grad_year')

                    # Query the athlete from the database, however, some fields may be empty
                    athlete = Athlete.query.filter_by(hawkins_id=hawkins_id, first_name=first_name, last_name=last_name, birth_date=birth_date, gender=gender, sport=sport, position=position, grad_year=grad_year).first()
                    if athlete is None:
                        athlete = Athlete.query.filter_by(hawkins_id=hawkins_id).first()
                        if athlete is None:
                            flash('Athlete not found!', 'error')
                            return render_template("add_athletes.html")
                    db.session.delete(athlete)
                    db.session.commit()
                    flash('Athlete deleted successfully!', 'success')
                else:
                    file = request.files['file']
                    if file.filename == '':
                        flash('No file selected!', 'error')
                        return render_template("add_athletes.html")
                    try:
                        file.save(file.filename)
                        with open(file.filename, 'r') as f:
                            lines = f.readlines()
                            # Skip the first line
                            lines = lines[1:]
                            for line in lines:
                                data = line.split(',')
                                if len(data) == 8:
                                    #check if athlete already exists
                                    #trim and remove quoatation marks
                                    data = [x.strip().replace('"', '').replace('\n','') for x in data]
                                    athlete = Athlete.query.filter_by(hawkins_id=data[0], first_name=data[1], last_name=data[2], birth_date=data[3], gender=data[4], sport=data[5], position=data[6], grad_year=data[7]).first()
                                    if athlete is not None:
                                        db.session.delete(athlete)
                            db.session.commit()
                            flash('Athletes deleted successfully!', 'success')
                        # Delete the file
                        file.close()
                        os.remove(file.filename)

                    except Exception as e:
                        print(e)
                        print(data)
                        flash('Error deleting athletes!', 'error')


    return render_template("add_athletes.html", links=get_links(current_user))


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