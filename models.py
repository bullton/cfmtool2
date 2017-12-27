# encoding: utf-8

from exts import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Source(db.Model):
    __tablename__ = 'source'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(50), nullable=False)
    upload_time = db.Column(db.DateTime,default=datetime.now)
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    owner = db.relationship('User',backref=db.backref('source'))