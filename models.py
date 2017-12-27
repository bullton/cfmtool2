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


class Rule(db.Model):
    __tablename__ = 'rule'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rulename = db.Column(db.String(50),unique=True, nullable=False)
    customer = db.Column(db.String(50), nullable=False)
    release = db.Column(db.String(50), nullable=False)
    customer_feature_white = db.Column(db.Text)
    customer_feature_black = db.Column(db.Text)
    customer_top_fault = db.Column(db.Text)
    customer_care_function = db.Column(db.Text)
    uuf_filter = db.Column(db.Text)
    uuf_exclusion = db.Column(db.Text)
    kpi_filter = db.Column(db.Text)
    kpi_exclusion = db.Column(db.Text)
    ca_filter = db.Column(db.Text)
    ca_exclusion = db.Column(db.Text)
    oamstab_filter = db.Column(db.Text)
    oamstab_exclusion = db.Column(db.Text)
    pet_filter = db.Column(db.Text)
    pet_exclusion = db.Column(db.Text)
    func_filter = db.Column(db.Text)
    func_exclusion = db.Column(db.Text)
    category_search_field = db.Column(db.Text)
    category_tag = db.Column(db.Text)
    customer_rru = db.Column(db.Text)
    customer_bbu = db.Column(db.Text)
    customer_keyword_white = db.Column(db.Text)
    customer_keyword_black = db.Column(db.Text)
    customer_pronto_white = db.Column(db.Text)
    customer_pronto_black = db.Column(db.Text)
    r4bbu = db.Column(db.Text)
    r3bbu = db.Column(db.Text)
    r2bbu = db.Column(db.Text)
    fsih = db.Column(db.Text)
    ftcomsc = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    owner = db.relationship('User', backref=db.backref('rule'))