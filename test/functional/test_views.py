import pytest
from flask import Flask
import flask_login as fl
from website import db
from website.models import Athlete, Team, Coach, User, Admin
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

def test_hawkin_coach(test_client, login_coach):
    response = test_client.get('/hawkin')
    assert response.status_code == 200
    assert b"Select Athlete" in response.data

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

    response = test_client.post(
        '/add_athletes',
        data={
            'action': 'delete',
            'hawkins_id': '69420'
        }
    )
    assert response.status_code == 200
    assert b"Athlete deleted successfully!" in response.data


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
    assert b"Coach added successfully!" in response.data

    response = test_client.post(
        '/add_coaches',
        data={
            'action': 'delete',
            'first_name': 'TestCoach',
            'last_name': 'Smith',
            'team': 'Football'
        }
    )
    assert response.status_code == 200
    assert b"Coach deleted successfully!" in response.data



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

    response = test_client.post(
        '/add_teams',
        data={
            'action': 'delete',
            'team_name': 'Testball',
            'sport': 'Testball'
        }
    )
    assert response.status_code == 200
    assert b"Team deleted successfully!" in response.data
    
def test_add_admins(test_client, login_SuperAdmin,new_session):
    # Test adding an admin
    response = test_client.post(
        '/add_admins',
        data={
            'action': 'add',
            'first_name': 'TestAdmin',
            'last_name': 'Smith',
        }
    )
    assert response.status_code == 200
    assert b"Admin added successfully!" in response.data

    response = test_client.post(
        '/add_admins',
        data={
            'action': 'delete',
            'first_name': 'TestAdmin',
            'last_name': 'Smith',
        }
    )
    assert response.status_code == 200
    assert b"Admin deleted successfully!" in response.data

def test_delete_athlete(test_client, login_SuperAdmin,new_session):
    # Test deleting an athlete
    athlete = Athlete('69422',
                      'TestGuy2',
                      'Athlete',
                      '2000-01-01',
                      'M',
                      'Football',
                      'Quarterback',
                      '2024')
    new_session.add(athlete)
    new_session.commit()

    response = test_client.post(
        '/add_athletes',
        data={
            'action': 'delete-dropdown',
            'delete_athlete': athlete.hawkins_id,
        }
    )
    assert response.status_code == 200
    assert b"Athlete deleted successfully!" in response.data

    deleted_athlete = new_session.query(Athlete).filter_by(hawkins_id='69422').first()
    assert deleted_athlete is None

def test_delete_coach(test_client, login_SuperAdmin,new_session):
    # Test deleting a coach
    coach = Coach(first_name="Coach696969", last_name="Test", team=new_session.query(Team).first())
    new_session.add(coach)
    new_session.commit()

    response = test_client.post(
        '/add_coaches',
        data={
            'action': 'delete-dropdown',
            'delete_coach': coach.id,
        }
    )
    assert response.status_code == 200
    assert b"Coach deleted successfully!" in response.data

    deleted_coach = new_session.query(Coach).filter_by(first_name='Coach696969').first()
    assert deleted_coach is None

def test_delete_team(test_client, login_SuperAdmin,new_session):
    # Test deleting a team
    team = Team(name='TestSportName',
                sport='TestSportSport')
    new_session.add(team)
    new_session.commit()

    response = test_client.post(
        '/add_teams',
        data={
            'action': 'delete-dropdown',
            'delete_team': team.id,
        }
    )
    assert response.status_code == 200
    assert b"Team deleted successfully!" in response.data

    deleted_team = new_session.query(Team).filter_by(name='TestSportName').first()
    assert deleted_team is None

def test_delete_admin(test_client, login_SuperAdmin,new_session):
    # Test deleting an admin
    admin = Admin(first_name="AdminLoser", last_name="User", email="adminloser@example.com")
    new_session.add(admin)
    new_session.commit()

    response = test_client.post(
        '/add_admins',
        data={
            'action': 'delete-dropdown',
            'delete_admin': admin.id,
        }
    )
    assert response.status_code == 200
    assert b"Admin deleted successfully!" in response.data

    deleted_admin = new_session.query(User).filter_by(first_name='AdminLoser').first()
    assert deleted_admin is None
        
def test_add_athletes_from_csv(test_client, login_SuperAdmin,new_session):
    # Test adding athletes from a CSV file
    csv_path = "csv/test_athlete.csv"
    with open(csv_path, 'rb') as csv_file:
        response = test_client.post(
            '/add_athletes',
            data={
                'action': 'add',
                'file': (csv_file, 'test_athlete.csv')
            }
        )
    assert response.status_code == 200
    assert b"Entities added successfully!" in response.data

    with open(csv_path, 'rb') as csv_file:
        response = test_client.post(
            '/add_athletes',
            data={
                'action': 'delete',
                'file': (csv_file, 'test_athlete.csv')
            }
        )
    assert response.status_code == 200
    assert b"Entities deleteed successfully!" in response.data

def test_add_coaches_from_csv(test_client, login_SuperAdmin,new_session):
    # Test adding coaches from a CSV file
    csv_path = "csv/test_coach.csv"
    with open(csv_path, 'rb') as csv_file:
        response = test_client.post(
            '/add_coaches',
            data={
                'action': 'add',
                'file': (csv_file, 'test_coach.csv')
            }
        )
    assert response.status_code == 200
    assert b"Entities added successfully!" in response.data

    with open(csv_path, 'rb') as csv_file:
        response = test_client.post(
            '/add_coaches',
            data={
                'action': 'delete',
                'file': (csv_file, 'test_coach.csv')
            }
        )
    assert response.status_code == 200
    assert b"Entities deleteed successfully!" in response.data

def test_add_teams_from_csv(test_client, login_SuperAdmin,new_session):
    # Test adding teams from a CSV file
    csv_path = "csv/test_team.csv"
    with open(csv_path, 'rb') as csv_file:
        response = test_client.post(
            '/add_teams',
            data={
                'action': 'add',
                'file': (csv_file, 'test_team.csv')
            }
        )
    assert response.status_code == 200
    assert b"Entities added successfully!" in response.data

    with open(csv_path, 'rb') as csv_file:
        response = test_client.post(
            '/add_teams',
            data={
                'action': 'delete',
                'file': (csv_file, 'test_team.csv')
            }
        )
    assert response.status_code == 200
    assert b"Entities deleteed successfully!" in response.data

def test_add_admins_from_csv(test_client, login_SuperAdmin,new_session):
    # Test adding admins from a CSV file
    csv_path = "csv/test_admin.csv"
    with open(csv_path, 'rb') as csv_file:
        response = test_client.post(
            '/add_admins',
            data={
                'action': 'add',
                'file': (csv_file, 'test_admin.csv')
            }
        )
    assert response.status_code == 200
    assert b"Entities added successfully!" in response.data

    with open(csv_path, 'rb') as csv_file:
        response = test_client.post(
            '/add_admins',
            data={
                'action': 'delete',
                'file': (csv_file, 'test_admin.csv')
            }
        )
    assert response.status_code == 200
    assert b"Entities deleteed successfully!" in response.data

def test_add_athletes_error(test_client, login_SuperAdmin,new_session):
    # Test adding an athlete that already exists
    response = test_client.post(
        '/add_athletes',
        data={
            'action': 'delete',
            'hawkins_id': '69425',
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
    assert b"Error" in response.data

def test_add_coaches_error(test_client, login_SuperAdmin,new_session):
    # Test adding a coach that already exists
    response = test_client.post(
        '/add_coaches',
        data={
            'action': 'delete',
            'first_name': 'TestCoachLoser',
            'last_name': 'Smith',
            'team': 'Football'
        }
    )
    assert response.status_code == 200
    assert b"Error" in response.data

def test_add_teams_error(test_client, login_SuperAdmin,new_session):
    # Test adding a team that already exists
    response = test_client.post(
        '/add_teams',
        data={
            'action': 'delete',
            'team_name': 'TestballtheSport',
            'sport': 'Testball'
        }
    )
    assert response.status_code == 200
    assert b"Error" in response.data

def test_add_admins_error(test_client, login_SuperAdmin,new_session):
    # Test adding an admin that already exists
    response = test_client.post(
        '/add_admins',
        data={
            'action': 'delete',
            'first_name': 'TestAdminLoserGuy',
            'last_name': 'Smith',
        }
    )
    assert response.status_code == 200
    assert b"Error" in response.data

def test_delete_athletes_error(test_client, login_SuperAdmin,new_session):
    # Test deleting an athlete that does not exist
    response = test_client.post(
        '/add_athletes',
        data={
            'action': 'delete-dropdown',
            'delete_athlete': '69425',
        }
    )
    assert response.status_code == 200
    assert b"Error" in response.data

def test_delete_coaches_error(test_client, login_SuperAdmin,new_session):
    # Test deleting a coach that does not exist
    response = test_client.post(
        '/add_coaches',
        data={
            'action': 'delete-dropdown',
            'delete_coach': '69425',
        }
    )
    assert response.status_code == 200
    assert b"Error" in response.data

def test_delete_teams_error(test_client, login_SuperAdmin,new_session):
    # Test deleting a team that does not exist
    response = test_client.post(
        '/add_teams',
        data={
            'action': 'delete-dropdown',
            'delete_team': '69425',
        }
    )
    assert response.status_code == 200
    assert b"Error" in response.data

def test_delete_admins_error(test_client, login_SuperAdmin,new_session):
    # Test deleting an admin that does not exist
    response = test_client.post(
        '/add_admins',
        data={
            'action': 'delete-dropdown',
            'delete_admin': '69425',
        }
    )
    assert response.status_code == 200
    assert b"Error" in response.data