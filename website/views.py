from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from website import db
from .models import Athlete, Team, TeamUserAssociation, Coach
import os
from hdforce import AuthManager
import hdforce as hd
import json
import numpy as np

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
            "url": url_for("main.index")
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

    if user.user_type == "super_admin":
        links += [
            {
                "name": "View/Edit Admins",
                "url": url_for("main.add_admins"),
                "icon": "images/admins.png"
            }
        ]

    links += [
        {
            "name": "Hawkins Dynamics",
            "url": url_for("main.hawkin"),
            "icon": "images/hawkin.jpg"
        }
    ]

    links += [
        {
            "name": "Logout",
            "url": url_for("auth.logout")
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

important_data = ['Braking RFD(N/s)','Jump Height(m)','mRSI','Peak Relative Propulsive Power(W/kg)']

def averagePoints(data):
    return_data = []
    iter = 0
    while (iter < len(data) - 1):
        return_data.append({})
        return_data[-1]['timestamp'] = data[iter]['timestamp']
        return_data[-1]['id'] = data[iter]['id']
        return_data[-1]['athlete_id'] = data[iter]['athlete_id']
        return_data[-1]['athlete_name'] = data[iter]['athlete_name']
        if abs(data[iter]['timestamp'] - data[iter+1]['timestamp']) < 36000:
            for data_point in important_data:
                if data[iter][data_point] != None and data[iter+1][data_point] != None:
                    return_data[-1][data_point] = (data[iter][data_point] + data[iter+1][data_point]) / 2
                elif data[iter][data_point] == None and data[iter+1][data_point] != None:
                    return_data[-1][data_point] = data[iter+1][data_point]
                elif data[iter][data_point] != None and data[iter+1][data_point] == None:
                    return_data[-1][data_point] = data[iter][data_point]
                else:
                    return_data[-1][data_point] = None
            iter += 2
        else:
            #`print(data[iter]['timestamp'], data[iter+1]['timestamp'])
            for data_point in important_data:
                return_data[-1][data_point] = data[iter][data_point]
            iter += 1
    #print(return_data)
    return return_data

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
    athlete_data.replace([np.nan, np.inf, -np.inf], None, inplace=True)

    athlete_data_list = athlete_data.to_dict(orient="records")

    return averagePoints(athlete_data_list)

def fix_team_names(athlete_team_name, gender):
    # there are inconsistencies in the database vs the athlete data, so we need to standardize the team names
    if "Lacrosse" in athlete_team_name:
            athlete_team_name = athlete_team_name.replace("Lacrosse", "LAX")
    elif "Women's Field Hockey" in athlete_team_name:
        athlete_team_name = "Field Hockey"
    elif "Alpine Skiing" in athlete_team_name:
        if gender == "M":
            athlete_team_name = "Men's Alpiine" #this is not my typo, this is how it is in the database
        else:
            athlete_team_name = "Women's Alpine"
    elif "Swimming & Diving" in athlete_team_name:
        if gender == "M":
            athlete_team_name = "Men's Swim & Dive"
        else:
            athlete_team_name = "Women's Swim & Dive"
    elif "Women's Volleyball" in athlete_team_name:
        athlete_team_name = "Volleyball"
    elif "Nordic Skiing" in athlete_team_name:
        if gender == "M":
            athlete_team_name = "Men's Nordic"
        else:
            athlete_team_name = "Women's Nordic"
    return athlete_team_name



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

    else: # admin or super admin
        all_teams = Team.query.all()
        # Check if no teams exist in the database
        if len(all_teams) == 0: #if there are no teams in the database, we need to add them. Doing this manually would be a pain, so we will do it automatically, this literally will only happen once
            all_athletes = Athlete.query.all()
            hd_teams = hd.GetTeams() #this is a pandas dataframe
            #theres a change that teams have spaces at the end of their names, so we need to strip them
            hd_teams['name'] = hd_teams['name'].str.strip()
            #print(hd_teams)
            allteamnames = {}
            teams = {}
        
            for athlete in all_athletes:
                athlete_team_name = athlete.sport

                athlete_team_name = fix_team_names(athlete_team_name, athlete.gender)
                
                if athlete_team_name not in allteamnames.keys():
                    try:
                        allteamnames[athlete_team_name] = [athlete]
                        #print(athlete_team_name)
                        #replace Lacrosse with LAX in any part of the string
                        hawkins_database_id = hd_teams.loc[hd_teams['name'] == athlete_team_name]['id'].values[0]
                        #print(hawkins_database_id)
                        team = Team(name=athlete_team_name, sport=athlete_team_name, hawkins_database_id=hawkins_database_id)
                        teams[athlete_team_name] = team
                        association = TeamUserAssociation(team=team, user=athlete)
                        db.session.add(team)
                        db.session.add(association)
                    except:
                        print(f"Could not find team {athlete_team_name} in Hawkins Dynamics database")
                else:
                    try:
                        allteamnames[athlete_team_name].append(athlete)
                        association = TeamUserAssociation(team=teams[athlete_team_name], user=athlete)
                        db.session.add(association)
                    except:
                        pass

                
            # Commit all changes to the database in one transaction
            db.session.commit()
            all_teams = Team.query.all()

        athletes = Athlete.query.all()
        data_list = {}
        for team in all_teams:
            #print(team.name)
            data_list[team.name.replace("'", "")] = []

        for athlete in athletes:
            athlete_team_name = fix_team_names(athlete.sport, athlete.gender)
            data_list[athlete_team_name.replace("'", "")].append(athlete.first_name.replace("'", "") + " " + athlete.last_name.replace("'", ""))
    
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
        file = request.files.get('file')
        delete_athlete = request.form.get('delete_athlete')

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

        elif file:
            if file.filename == '':
                flash('No file selected!', 'error')
            else:
                process_csv(file, action)

        elif delete_athlete:
            athlete = Athlete.query.filter_by(hawkins_id=delete_athlete).first()
            try:
                if action == 'delete-dropdown' and athlete:
                    db.session.delete(athlete)
                    flash('Athlete deleted successfully!', 'success')
                db.session.commit()
            except Exception:
                flash(f'Error {action}ing athlete!', 'error')

    raw_athletes = Athlete.query.all()
    athletes = []

    for raw_athlete in raw_athletes:
        athletes.append({
            'name': f'{raw_athlete.first_name} {raw_athlete.last_name}',
            'id': raw_athlete.hawkins_id
        })
    
    return render_template("add_athletes.html", links=get_links(current_user), athletes=athletes)

@main_blueprint.route('/add_coaches', methods=['GET', 'POST'])
@login_required
def add_coaches():
    if request.method == 'POST' and 'action' in request.form:
        action = request.form.get('action')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        file = request.files.get('file')

        delete_coach = request.form.get('delete_coach')
        
        if first_name:
            form_data = {
                'first_name': first_name,
                'last_name': request.form.get('last_name'),
                'team': request.form.get('team')
            }
            coach = Coach.query.filter_by(first_name=first_name, last_name=last_name).first()
            try:
                if action == 'add' and not coach:
                    team = Team.query.filter_by(name=form_data['team']).first()
                    db.session.add(Coach(**form_data, team=team))
                    flash('Coach added successfully!', 'success')
                elif action == 'delete' and coach:
                    db.session.delete(coach)
                    flash('Coach deleted successfully!', 'success')
                db.session.commit()
            except Exception:
                flash(f"Error {action}ing coach!", 'error')
        elif file:
            if file.filename == '':
                flash('No file selected!', 'error')
            else:
                process_csv(file, action)

        elif delete_coach:
            coach = Coach.query.filter_by(id=delete_coach).first()
            try:
                if action == 'delete-dropdown' and coach:
                    db.session.delete(coach)
                    flash('Coach deleted successfully!', 'success')
                db.session.commit()
            except Exception:
                flash(f'Error {action}ing coach!', 'error')

    teams = Team.query.all()
    #make a dictionary of teams
    teams_dict = []
    for team in teams:
        teams_dict.append({'team_name': team.name})

    raw_coaches = Coach.query.all()
    coaches = []

    for raw_coach in raw_coaches:
        coaches.append({
            'name': f'{raw_coach.first_name} {raw_coach.last_name}',
            'id': raw_coach.id
        })

    return render_template("add_coaches.html", links=get_links(current_user), teams=teams_dict, coaches=coaches)

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
                elif len(data) == 3:
                    team = Team.query.filter_by(name=data[2]).first()
                    coach = Coach.query.filter_by(first_name=data[0], last_name=data[1]).first()
                    if action == 'add' and coach is None:
                        db.session.add(Coach(first_name=data[0], last_name=data[1], team=team))
                    elif action == 'delete' and coach:
                        db.session.delete(coach)

                elif len(data) == 1: # we like, andy???
                    team = Team.query.filter_by(name=data[0]).first()
                    if action == 'add' and team is None:
                        db.session.add(Team(name=data[0], sport=data[0]))
                    elif action == 'delete' and team:
                        db.session.delete(team)

        db.session.commit()
        flash(f"Entities {action}ed successfully!", 'success')
        os.remove(file.filename)
    except Exception as e:
        flash(f"Error {action}ing entities!", 'error')
        print(e, data)

@main_blueprint.route('/add_teams', methods=['GET', 'POST'])
@login_required
def add_teams():
    if request.method == 'POST' and 'action' in request.form:
        action = request.form.get('action')

        team_name = request.form.get('team_name')
        file = request.files.get('file')
        delete_team = request.form.get('delete_team')
        
        if team_name:
            team = Team.query.filter_by(name=team_name).first()
            try:
                if action == 'add' and not team:
                    db.session.add(Team(name=team_name, sport=team_name))
                    flash('Team added successfully!', 'success')
                elif action == 'delete' and team:
                    db.session.delete(team)
                    flash('Team deleted successfully!', 'success')
                db.session.commit()
            except Exception:
                flash(f"Error {action}ing team!", 'error')
        elif file:
            if file.filename == '':
                flash('No file selected!', 'error')
            else:
                process_csv(file, action)

        elif delete_team:
            team = Team.query.filter_by(id=delete_team).first()
            try:
                if action == 'delete-dropdown' and team:
                    db.session.delete(team)
                    flash('Team deleted successfully!', 'success')
                db.session.commit()
            except Exception:
                flash(f'Error {action}ing team!', 'error')

    raw_teams = Team.query.all()
    teams = []

    for raw_team in raw_teams:
        teams.append({
            'name': raw_team.name,
            'id': raw_team.id
        })

    return render_template("add_teams.html", links=get_links(current_user), teams=teams)

@main_blueprint.route('/add_admins', methods=['GET'])
@login_required
def add_admins():
    pass
