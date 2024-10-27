from models import db, Admin
from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_admin_user(colby_id, first_name, last_name, email):
    with app.app_context():
        # Check if an admin already exists with the given colby_id or email
        if Admin.query.filter_by(colby_id=colby_id).first() or Admin.query.filter_by(email=email).first():
            print("Admin with this Colby ID or email already exists.")
            return

        # Create and add the admin user
        admin = Admin(colby_id=colby_id, first_name=first_name, last_name=last_name, email=email)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{first_name} {last_name}' created successfully.")

# Example usage in command prompt
# Run this script directly to create an admin user
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created

    # Replace the following details with your desired admin info
    create_admin_user(
        colby_id=762460,
        first_name="Andrew",
        last_name="Lipton",
        email="awlipt26@colby.edu"
    )
