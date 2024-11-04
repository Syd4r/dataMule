from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from models import db, Athlete, Team, TeamUserAssociation
import os
from hdforce import AuthManager
import hdforce as hd
import json
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Create a blueprint
main_blueprint = Blueprint('main', __name__)

AuthManager(
    region='Americas',
    authMethod='env',
    refreshToken_name='HD_REFRESH_TOKEN',
    refreshToken=os.getenv('HD_REFRESH_TOKEN')
)

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

def getUserData(user):
    if user.hawkins_database_id == 'notSet':
        name = user.first_name + " " + user.last_name
        all_athletes = hd.GetAthletes()
        athlete = all_athletes.loc[all_athletes['name'] == name]
        try:
            id = athlete['id'].values[0]
            user.hawkins_database_id = id
            db.session.commit()
        except:
            print(f"Could not find athlete {name} in Hawkins Dynamics database")
            return []
    else:
        id = user.hawkins_database_id

    athlete_data = hd.GetTests(athleteId=id)
    athlete_data_list = athlete_data.to_dict(orient="records")
    
    athlete_data.replace([np.nan, np.inf, -np.inf], None, inplace=True)

    athlete_data_list = athlete_data.to_dict(orient="records")

    return athlete_data_list

@main_blueprint.route('/hawkin', methods=['GET'])
@login_required
def hawkin():
    user = current_user
    #user = db.session.query(Athlete).filter_by(first_name="Duke", last_name="Ferrara").first() # USE THIS LINE ONLY FOR TESTING
    if user.user_type == "athlete":
        data_list = getUserData(user)
    elif user.user_type == "coach":
        team = user.team
        athletes = team.members
        data_list = []
        #data_list["Name"] = team.name.replace("'", "")
        for athlete in athletes:
            athlete = athlete.user
            data_list.append(athlete.first_name.replace("'", "") + " " + athlete.last_name.replace("'", ""))
    else:
        all_teams = Team.query.all()
        # Check if no teams exist in the database
        if len(all_teams) == 0:
            all_athletes = Athlete.query.all()
        
            for athlete in all_athletes:
                athlete_team_name = athlete.sport 
                
                # Check if the team already exists
                team = Team.query.filter_by(name=athlete_team_name).first()
                
                # If team doesn't exist, create it
                if not team:
                    team = Team(name=athlete_team_name, sport=athlete_team_name)
                    db.session.add(team)
                    db.session.flush()  # Ensures team.id is available without committing

                # Check if the athlete is already associated with this team
                association_exists = TeamUserAssociation.query.filter_by(team_id=team.id, user_id=athlete.id).first()
                
                # If not already associated, add the athlete to the team
                if not association_exists:
                    association = TeamUserAssociation(team_id=team.id, user_id=athlete.id, role="athlete")
                    db.session.add(association)
            # Commit all changes to the database in one transaction
            db.session.commit()
            all_teams = Team.query.all()
    
        data_list = {}
        for team in all_teams:
            data_list[team.name.replace("'", "")] = []
            athletes = team.members
            for athlete in athletes:
                athlete = athlete.user
                data_list[team.name.replace("'", "")].append(athlete.first_name.replace("'", "") + " " + athlete.last_name.replace("'", ""))
    return render_template("hawkin.html", athlete_data=json.dumps(data_list), links=get_links(user), user_type=user.user_type)

@main_blueprint.route('/get_athlete_data/<user_name>', methods=['GET'])
@login_required
def get_athlete_data(user_name):
    user = db.session.query(Athlete).filter_by(first_name=user_name.split('-')[0], last_name=user_name.split('-')[1]).first()
    data_list = getUserData(user)
    return json.dumps(data_list)


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
