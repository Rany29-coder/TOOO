from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    projects = db.relationship('Project', back_populates='user')
    categories = db.relationship('Category', back_populates='user')

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='projects')
    columns = db.relationship('Column', back_populates='project')

class Column(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    order = db.Column(db.Integer)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', back_populates='columns')
    tasks = db.relationship('Task', back_populates='column')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    picture = db.Column(db.String(250))
    date = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    pomodoros = db.Column(db.Integer)
    priority = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    description = db.Column(db.String(1000))
    column_id = db.Column(db.Integer, db.ForeignKey('column.id'))
    column = db.relationship('Column', back_populates='tasks')
    parent_task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    subtasks = db.relationship('Task', backref=db.backref('parent', remote_side=[id]))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='categories')
