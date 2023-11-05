import pytest
from app import create_app, db 
from app.models import User

@pytest.fixture(scope='module')
def test_app():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    with app.app_context():
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def test_client(test_app):
    with test_app.test_client() as testing_client:
        with test_app.app_context():
            user = User(username='test_user', password='Password')
            db.session.add(user)
            db.session.commit()
            
        yield testing_client

@pytest.fixture(scope='module')
def init_database(test_app):
    with test_app.app_context():
        db.create_all(app=test_app)

