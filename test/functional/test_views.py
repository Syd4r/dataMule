import pytest
from flask import Flask
import flask_login as fl
from website import db
from website.models import Athlete, Team, Coach, User
import os

def test_index(test_client, login_user):
    # Test the index route
    response = test_client.get('/')
    assert b"test user" in response.data  # Ensure user data is in the response
    assert response.status_code == 200

def test_hawkin_athlete_page(test_client, login_athlete):
    # Test /hawkin route for an athlete user

    response = test_client.get('/hawkin')
    assert response.status_code == 200
    assert b"Hawkin Dynamics Data" in response.data

def test_get_athlete_data_no_id(test_client,new_session,login_SuperAdmin):
    new_athlete = Athlete(
        hawkins_id="69696969", first_name="Stupid", last_name="Athlete",
        birth_date="2000-01-01", gender="M", sport="Testing",
        position="Tester", grad_year=2024
    )
    new_athlete.email = "newathlete@new.com"
    new_session.add(new_athlete)
    new_session.commit()

    response = test_client.get('/get_athlete_data/Stupid-Athlete',follow_redirects=True)
    retrieved = new_session.query(Athlete).filter_by(hawkins_id="69696969").first()
    new_session.delete(new_athlete)
    new_session.commit()
    assert response.status_code == 200 
    assert b"[]" in response.data

def test_get_athlete_data_valid_id(test_client,new_session,login_SuperAdmin):

    retrieved = new_session.query(Athlete).first()
    response = test_client.get(f'/get_athlete_data/{retrieved.first_name}-{retrieved.last_name}',follow_redirects=True)

    assert response.status_code == 200 
    assert b"timestamp" in response.data #assume the dataframe coming from HDforce has a timestamp variable



def test_hawkin_admin_data(test_client, login_SuperAdmin):
    # Test /hawkin route for an admin user
    response = test_client.get('/hawkin')
    assert response.status_code == 200
    assert b"Select Team" in response.data


def test_add_athletes(test_client, login_SuperAdmin ,new_session):
    # Test adding an athlete
    response = test_client.post(
        '/add_athletes',
        data={
            'action': 'add',
            'hawkins_id': '69420',
            'first_name': 'Test',
            'last_name': 'Athlete',
            'birth_date': '2000-01-01',
            'gender': 'M',
            'sport': 'Football',
            'position': 'Quarterback',
            'grad_year': '2024',
        }
    )
    assert response.status_code == 200
    assert b"Athlete added successfully!" in response.data

    just_added = new_session.query(Athlete).filter_by(hawkins_id='69420').first()
    new_session.delete(just_added)
    new_session.commit()


def test_add_coaches(test_client,login_SuperAdmin,new_session):
    # Test adding a coach
    response = test_client.post(
        '/add_coaches',
        data={
            'action': 'add',
            'first_name': 'TestCoach',
            'last_name': 'Smith',
            'team': 'Football'
        }
    )
    assert response.status_code == 200
    assert b"Error adding coach" in response.data
    #assert b"Coach added successfully!" in response.data

    added_coach = new_session.query(Coach).filter_by(first_name='TestCoach').first()
    if added_coach:
        new_session.delete(added_coach)
        new_session.commit()

def test_add_teams(test_client, login_SuperAdmin,new_session):
    # Test adding a team
    response = test_client.post(
        '/add_teams',
        data={
            'action': 'add',
            'team_name': 'Testball',
            'sport': 'Testball'
        }
    )
    assert response.status_code == 200
    assert b"Team added successfully!" in response.data

    added_team = new_session.query(Team).filter_by(name="Testball").first()
    new_session.delete(added_team)
    new_session.commit()
    


def test_delete_athletes(test_client, login_SuperAdmin,new_session):
    # Test deleting an athlete
    athlete = Athlete(
        hawkins_id='12345',
        first_name='John',
        last_name='Doe',
        birth_date='2000-01-01',
        gender='M',
        sport='Football',
        position='Quarterback',
        grad_year='2024'
    )
    new_session.add(athlete)
    new_session.commit()

    # Now delete the athlete
    response = test_client.post(
        '/add_athletes',
        data={
            'action': 'delete',
            'hawkins_id': '12345'
        }
    )
    assert response.status_code == 200
    assert b"Athlete deleted successfully!" in response.data

    if athlete:
        new_session.delete(athlete)
        new_session.commit()

