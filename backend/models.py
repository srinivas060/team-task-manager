from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20), default='member')

    tasks = db.relationship('Task', backref='assigned_user')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(300))

    tasks = db.relationship('Task', backref='project')


class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100))

    description = db.Column(db.String(300))

    status = db.Column(db.String(50), default='Pending')

    due_date = db.Column(db.String(50))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))