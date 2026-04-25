import pytest
from app import create_app, db as _db

# Import models so they register with db.Model before create_all() runs
import models  # noqa: F401

@pytest.fixture
def app():
    app = create_app('config.Config')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
