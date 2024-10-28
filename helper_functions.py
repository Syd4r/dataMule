from models import db, Admin, Athlete
from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_admin_user(first_name, last_name, email, password):
    with app.app_context():
        # Check if an admin already exists with the given email
        if Admin.query.filter_by(email=email).first():
            print("Admin with this email already exists.")
            return

        # Create and add the admin user
        admin = Admin(first_name=first_name, last_name=last_name, email=email)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{first_name} {last_name}' created successfully.")

def create_athlete_user(first_name, last_name, hawkins_id, birth_date, gender, sport, position, grad_year):
    with app.app_context():
        # Check if an athlete already exists with the given email
        if Athlete.query.filter_by(hawkins_id=hawkins_id).first():
            print("Athlete with this hawkins_id already exists.")
            return

        # Create and add the athlete user
        athlete = Athlete(first_name=first_name, last_name=last_name, hawkins_id=hawkins_id, birth_date=birth_date, gender=gender, sport=sport, position=position, grad_year=grad_year)
        db.session.add(athlete)
        db.session.commit()
        print(f"Athlete user '{first_name} {last_name}' created successfully.")


# Example usage in command prompt
# Run this script directly to create an admin user
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created

    # Replace the following details with your desired admin info
    create_admin_user(
        first_name="John",
        last_name="Doe",
        email="test@test",
        password="test"
    )

    # Replace the following details with your desired athlete info
    create_athlete_user(
        first_name="Andrew", #this needed to activate account
        last_name="Lipton", #this needed to activate account
        hawkins_id="123",
        birth_date="09/14/2004", #this needed to activate account
        gender="M",
        sport="Football",
        position="QB",
        grad_year=2028
    )