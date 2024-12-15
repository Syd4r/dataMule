
'''Scripts to initally set up the database'''
import os
import json
import numpy as np
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from website import db
from website.models import Athlete, Team, TeamUserAssociation, Coach, Admin
from website.views import fix_team_names
from hdforce import AuthManager
import hdforce as hd

import os
import time
import datetime
from hdforce import AuthManager
import hdforce as hd
from dotenv import load_dotenv

load_dotenv()

AuthManager(
    region='Americas',
    authMethod='env',
    refreshToken_name='HD_REFRESH_TOKEN',
    refreshToken=os.getenv('HD_REFRESH_TOKEN')
)

hdTeams = hd.GetTeams()
teamID = hdTeams.loc[hdTeams['name'] == 'Football']['id'].values[0]
print(teamID)

def epoch_time(month, day, year):
    '''Function to convert a date to epoch time'''
    return int(time.mktime(datetime.datetime(year, month, day).timetuple()))

#get the tests in chunks by year
for eachYear in range(2021, 2024):
    #create function to convert to epoch time
    fromTime = epoch_time(1, 1, eachYear)
    toTime = epoch_time(1, 1, eachYear+1)
    print(fromTime, toTime)
    tests = hd.GetTests(teamId= teamID, from_=fromTime, to_=toTime)
    print(tests)

def populate_teams():
        if (
            len(all_teams) == 0
        ):  # if there are no teams in the database, we need to add them. Doing this manually would be a pain, so we will do it automatically, this literally will only happen once
            all_athletes = Athlete.query.all()
            hd_teams = hd.GetTeams()  # this is a pandas dataframe
            # theres a change that teams have spaces at the end of their names, so we need to strip them
            hd_teams["name"] = hd_teams["name"].str.strip()
            # print(hd_teams)
            allteamnames = {}
            teams = {}

            for athlete in all_athletes:
                athlete_team_name = athlete.sport

                athlete_team_name = fix_team_names(athlete_team_name, athlete.gender)

                if athlete_team_name not in allteamnames.keys():
                    try:
                        allteamnames[athlete_team_name] = [athlete]
                        # print(athlete_team_name)
                        # replace Lacrosse with LAX in any part of the string
                        hawkins_database_id = hd_teams.loc[
                            hd_teams["name"] == athlete_team_name
                        ]["id"].values[0]
                        # print(hawkins_database_id)
                        team = Team(
                            name=athlete_team_name,
                            sport=athlete_team_name,
                            hawkins_database_id=hawkins_database_id,
                        )
                        teams[athlete_team_name] = team
                        association = TeamUserAssociation(team=team, user=athlete)
                        db.session.add(team)
                        db.session.add(association)
                    except:
                        print(
                            f"Could not find team {athlete_team_name} in Hawkins Dynamics database"
                        )
                else:
                    try:
                        allteamnames[athlete_team_name].append(athlete)
                        association = TeamUserAssociation(
                            team=teams[athlete_team_name], user=athlete
                        )
                        db.session.add(association)
                    except:
                        pass

            # Commit all changes to the database in one transaction
            db.session.commit()
            all_teams = Team.query.all()