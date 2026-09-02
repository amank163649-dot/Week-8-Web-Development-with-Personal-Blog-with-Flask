import pytest
from app import create_app, db
from app.models import User, Post
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def new_user(app):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def new_post(app, new_user):
    post = Post(title='Test Post', content='<p>Test content</p>', author=new_user)
    db.session.add(post)
    db.session.commit()
    return post


def login(client, username='testuser', password='password123'):
    return client.post('/auth/login', data={
        'username': username,
        'password': password,
    }, follow_redirects=True)
