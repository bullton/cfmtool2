# encoding = utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    HOSTNAME = '127.0.0.1'
    PORT = '3306'
    DATABASE = 'db_flask'
    USERNAME = 'root'
    PASSWORD = 'root'
    DB_URI = 'mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
    SQLALCHEMY_DATABASE_URI = DB_URI

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}

