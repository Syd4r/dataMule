# Imports
from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

# Database Models
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    colby_id = db.Column(db.Integer, unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    user_type = db.Column(db.String(50), nullable=False)  # For polymorphic identity

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
    status = db.Column(db.String(20))  # Use descriptive strings
    gender = db.Column(db.String(10))
    class_year = db.Column(db.Integer)
    position = db.Column(db.String(50))
    hawkin_api_id = db.Column(db.String(100), nullable=True)

    date = db.Column(db.Date, nullable=True, default=datetime.utcnow)
    jump_height = db.Column(db.Float, nullable=True)
    braking_rfd = db.Column(db.Float, nullable=True)
    mrsi = db.Column(db.Float, nullable=True)
    peak_propulsive_force = db.Column(db.Float, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'athlete',
    }

    def __repr__(self):
        return f"<Athlete {self.first_name} {self.last_name}, Colby ID: {self.colby_id}>"
    
    def get_performance(self):
        return {
            'date': self.date,
            'jump_height': self.jump_height,
            'braking_rfd': self.braking_rfd,
            'mrsi': self.mrsi,
            'peak_propulsive_force': self.peak_propulsive_force
        }


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
