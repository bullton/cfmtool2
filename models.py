# encoding: utf-8

from exts import db
from datetime import datetime
from sqlalchemy.dialects.mysql import LONGTEXT


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


class Rule(db.Model):
    __tablename__ = 'rule'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rulename = db.Column(db.String(50),unique=True, nullable=False)
    customer = db.Column(db.String(50), nullable=False)
    release = db.Column(db.String(50), nullable=False)
    rules = db.Column(LONGTEXT)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User', backref=db.backref('rule'))
    parameter_id = db.Column(db.Integer, db.ForeignKey('parameters.id'))
    useparameter = db.relationship('Parameters', backref=db.backref('rule'))

class Static_Data(db.Model):
    __tablename__ = 'static_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(LONGTEXT)
    static_time = db.Column(db.DateTime,default=datetime.now)
    use_rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'))
    use_rule = db.relationship('Rule', backref=db.backref('static_data'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User', backref=db.backref('static_data'))

class Parameters(db.Model):
    __tablename__ = 'parameters'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text)
    release = db.Column(db.Text)
    customer = db.Column(db.Text)
    parameters = db.Column(LONGTEXT)
    insert_time = db.Column(db.DateTime,default=datetime.now)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User', backref=db.backref('parameters'))