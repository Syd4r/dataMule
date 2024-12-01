from website.models import User, Admin, Athlete, Coach, Team, TeamUserAssociation, AthletePerformance, Note

def test_user_creation(session):
    # Create a basic user
    user = User(first_name="test", last_name="user", email="testuser@test.com", user_type="user")
    user.set_password("securepassword")
    session.add(user)
    
    retrieved = session.query(User).filter_by(first_name="test").first()
    assert user.id is not None
    assert retrieved.first_name == "test"
    assert retrieved.last_name == "user"
    assert retrieved.email == "testuser@test.com"
    assert retrieved.user_type == "user"
    session.rollback()

def test_admin_creation(session):
    # Create an Admin user
    admin = Admin(first_name="Admin", last_name="User", email="admin@example.com")
    session.add(admin)

    retrieved = session.query(Admin).filter_by(email="admin@example.com").first()

    assert admin.id is not None
    assert admin.user_type == "admin"
    assert retrieved.first_name == "Admin"
    assert retrieved.last_name == "User"
    assert retrieved.email == "admin@example.com"
    assert retrieved.user_type == "admin"
    session.rollback()


def test_athlete_creation(session):
    # Create an Athlete user
    athlete = Athlete(
        hawkins_id="H1234", first_name="Test", last_name="Athlete",
        birth_date="2000-01-01", gender="M", sport="Testing",
        position="Tester", grad_year=2024
    )
    session.add(athlete)

    retrieved = session.query(Athlete).filter_by(hawkins_id="H1234").first()

    assert athlete.id is not None
    assert retrieved.user_type == "athlete"
    assert retrieved.sport == "Testing"
    session.rollback()

def test_coach_and_team_relationship(session):
    # Create a Team and Coach
    team = Team(name="TestTeam", sport="Balling")
    coach = Coach(first_name="Coach6969", last_name="Test", team=team)
    session.add(team)
    session.add(coach)

    retreived_team = session.query(Team).filter_by(name="TestTeam").first()
    retreived_coach = session.query(Coach).filter_by(first_name="Coach6969").first()

    assert coach.id is not None
    assert team.coach == coach
    assert coach.team == team
    assert retreived_team.coach == coach
    assert retreived_coach.team == team
    session.rollback()


def test_team_user_association(session):
    # Create Team and User
    team = Team(name="Test", sport="TestBall")
    user = User(first_name="Player", last_name="One", email="player1@example.com", user_type="user")
    association = TeamUserAssociation(team=team, user=user, role="Player")
    session.add_all([team, user, association])

    assoc = session.query(TeamUserAssociation).filter_by(team=team).first()

    assert association.team == team
    assert association.user == user
    assert len(team.members) == 1
    assert team.members[0].role == "Player"
    assert assoc.team == team
    assert assoc.user == user
    session.rollback()

def test_athlete_performance(session):
    # Create Athlete and Performance record
    athlete1 = Athlete(
        hawkins_id="H5678", first_name="Mark", last_name="Lee",
        birth_date="1999-05-05", gender="M", sport="Track", position="Runner", grad_year=2023
    )
    session.add(athlete1)
    performance = AthletePerformance(
        athlete=athlete1, jump_height=69420, braking_rfd=150.0, mrsi=1.2, peak_propulsive_force=300.0
    )
    session.add(performance)

    retreived_performance = session.query(AthletePerformance).filter_by(jump_height=69420).first()

    assert retreived_performance.jump_height == 69420 
    session.rollback()