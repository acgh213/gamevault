import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///gamevault.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IGDB_CLIENT_ID = os.environ.get('IGDB_CLIENT_ID', '')
    IGDB_CLIENT_SECRET = os.environ.get('IGDB_CLIENT_SECRET', '')
