import os
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

DATABASE_URL = 'postgresql://{}/{}'.format('localhost:5432', 'chatapp_db')
db = SQLAlchemy()


def db_setup(app, database_path=DATABASE_URL):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    db.create_all()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    admin = db.Column(db.Integer)
    users = db.Column(db.ARRAY(db.Integer()))
    create_time = db.Column(db.DateTime)