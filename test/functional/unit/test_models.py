from website.models import User, Admin, Athlete, Coach, Team, TeamUserAssociation, AlthetePerformance, Note

def test_user_creation(session):
    # Create a basic user
    user = User(first_name="John", last_name="Doe", email="john.doe@example.com", user_type="user")
    user.set_password("securepassword")
    session.add(user)
    session.commit()

    assert user.id is not None
    assert user.password_hash != "securepassword"  # Password should be hashed

def test_admin_creation(session):
    # Create an Admin user
    admin = Admin(first_name="Admin", last_name="User", email="admin@example.com")
    session.add(admin)
    session.commit()

    assert admin.id is not None
    assert admin.user_type == "admin"

def test_athlete_creation(session):
    # Create an Athlete user
    athlete = Athlete(
        hawkins_id="H1234", first_name="Jane", last_name="Doe",
        birth_date="2000-01-01", gender="F", sport="Soccer",
        position="Forward", grad_year=2024
    )
    session.add(athlete)
    session.commit()

    assert athlete.id is not None
    assert athlete.user_type == "athlete"
    assert athlete.sport == "Soccer"

def test_coach_and_team_relationship(session):
    # Create a Team and Coach
    team = Team(name="Team A", sport="Basketball")
    coach = Coach(first_name="Coach", last_name="Smith", team=team)
    session.add(team)
    session.add(coach)
    session.commit()

    assert coach.id is not None
    assert team.coach == coach
    assert coach.team == team

def test_team_user_association(session):
    # Create Team and User
    team = Team(name="Team B", sport="Baseball")
    user = User(first_name="Player", last_name="One", email="player1@example.com", user_type="user")
    association = TeamUserAssociation(team=team, user=user, role="Player")
    session.add_all([team, user, association])
    session.commit()

    assert association.team == team
    assert association.user == user
    assert len(team.members) == 1
    assert team.members[0].role == "Player"

def test_athlete_performance(session):
    # Create Athlete and Performance record
    athlete = Athlete(
        hawkins_id="H5678", first_name="Mark", last_name="Lee",
        birth_date="1999-05-05", gender="M", sport="Track", position="Runner", grad_year=2023
    )
    performance = AlthetePerformance(
        athlete=athlete, jump_height=2.5, braking_rfd=150.0, mrsi=1.2, peak_propulsive_force=300.0
    )
    session.add_all([athlete, performance])
    session.commit()

    assert len(athlete.athlete_performance) == 1
    assert athlete.athlete_performance[0].jump_height == 2.5

def test_note_creation(session):
    # Create a Note
    creator = User(first_name="Admin", last_name="Smith", email="admin@example.com", user_type="admin")
    receiver = Athlete(
        hawkins_id="H91011", first_name="Sarah", last_name="Connor",
        birth_date="2001-08-15", gender="F", sport="Tennis", position="Player", grad_year=2025
    )
    note = Note(text="Good job on the last performance.", creator=creator, receiver=receiver)
    session.add_all([creator, receiver, note])
    session.commit()

    assert note.id is not None
    assert note.creator == creator
    assert note.receiver == receiver
    assert receiver.received_notes[0].text == "Good job on the last performance."
