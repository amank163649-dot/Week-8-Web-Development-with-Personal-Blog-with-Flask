from app.models import User
from tests.conftest import login


def test_register_page_loads(client):
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Create an Account' in response.data


def test_register_new_user(client, app):
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'password2': 'password123',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert User.query.filter_by(username='newuser').first() is not None


def test_register_duplicate_username(client, new_user):
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'different@example.com',
        'password': 'password123',
        'password2': 'password123',
    })
    assert b'already taken' in response.data


def test_login_success(client, new_user):
    response = login(client)
    assert response.status_code == 200
    assert b'Welcome back' in response.data


def test_login_invalid_password(client, new_user):
    response = login(client, password='wrongpassword')
    assert b'Invalid username or password' in response.data


def test_logout(client, new_user):
    login(client)
    response = client.get('/auth/logout', follow_redirects=True)
    assert b'logged out' in response.data


def test_protected_route_redirects_when_logged_out(client):
    response = client.get('/posts/new', follow_redirects=True)
    assert b'Please log in' in response.data or b'Sign In' in response.data
