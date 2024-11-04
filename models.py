# Imports
from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# Database Models
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)
    user_type = db.Column(db.String(50), nullable=False)  # For polymorphic identity
    password_hash = db.Column(db.String(100), nullable=False, default='passwordNeedsToBeSet')  # Default password

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

    team_associations = db.relationship('TeamUserAssociation', back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}, ID: {self.id}, Type: {self.user_type}>"
    
    def check_colby_id(self, colby_id):
        colby_id = int(colby_id)
        return self.colby_id == colby_id
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)



class Admin(User):
    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

class SuperAdmin(User):
    __mapper_args__ = {
        'polymorphic_identity': 'super_admin',
    }


class Peak(User):
    __mapper_args__ = {
        'polymorphic_identity': 'peak',
    }


class Coach(User):
    __mapper_args__ = {
        'polymorphic_identity': 'coach',
    }


class Athlete(User):
    __tablename__ = 'athletes'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)  # Reuse primary key from User
    hawkins_id = db.Column(db.String(100))
    hawkins_database_id = db.Column(db.String(100), default='notSet')
    birth_date = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    sport = db.Column(db.String(50))
    position = db.Column(db.String(50))
    grad_year = db.Column(db.Integer)

    athlete_performance = db.relationship('AlthetePerformance', backref='athlete', cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_identity': 'athlete',
    }

    def __repr__(self):
        return f"<Athlete {self.first_name} {self.last_name}, Colby ID: {self.colby_id}>"
    
    def __init__(self, hawkins_id, first_name, last_name, birth_date, gender, sport, position, grad_year):
        self.hawkins_id = hawkins_id
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.gender = gender
        self.sport = sport
        self.position = position
        self.grad_year = grad_year
    
class AlthetePerformance(db.Model):
    date = db.Column(db.Date, nullable=True, default=datetime.utcnow)
    jump_height = db.Column(db.Float, nullable=True)
    braking_rfd = db.Column(db.Float, nullable=True)
    mrsi = db.Column(db.Float, nullable=True)
    peak_propulsive_force = db.Column(db.Float, nullable=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athletes.id'), primary_key=True)

    def __repr__(self):
        return f"<Performance for Athlete ID: {self.athlete_id}, Date: {self.date}>"
    


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    sport = db.Column(db.String(50), nullable=False)
    members = db.relationship('TeamUserAssociation', back_populates="team", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Team {self.name}, Sport: {self.sport}>"
    
class TeamUserAssociation(db.Model):
    __tablename__ = 'team_user_association'

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role = db.Column(db.String(50), nullable=False)

    team = db.relationship('Team', back_populates="members")
    user = db.relationship('User', back_populates="team_associations")

    def __repr__(self):
        return f"<Association Team ID: {self.team_id}, User ID: {self.user_id}, Role: {self.role}>"

class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('athletes.id', ondelete='CASCADE'))

    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_notes')
    receiver = db.relationship('Athlete', foreign_keys=[receiver_id], backref='received_notes')

    def __repr__(self):
        return f"<Note ID: {self.id}, Creator ID: {self.creator_id}, Receiver ID: {self.receiver_id}>"
