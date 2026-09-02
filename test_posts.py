from app.models import Post
from tests.conftest import login


def test_home_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'My Personal Blog' in response.data


def test_post_detail_view_increments_views(client, new_post):
    response = client.get(f'/posts/{new_post.id}')
    assert response.status_code == 200
    assert new_post.title.encode() in response.data


def test_post_detail_404_for_missing_post(client):
    response = client.get('/posts/9999')
    assert response.status_code == 404


def test_create_post_requires_login(client):
    response = client.get('/posts/new', follow_redirects=True)
    assert b'Sign In' in response.data


def test_create_post_success(client, new_user):
    login(client)
    response = client.post('/posts/new', data={
        'title': 'A Brand New Post',
        'summary': 'A short summary',
        'content': 'Post body content',
        'category': 0,
        'tags': 'flask, testing',
        'published': True,
    }, follow_redirects=True)

    assert response.status_code == 200
    post = Post.query.filter_by(title='A Brand New Post').first()
    assert post is not None
    assert post.author.username == 'testuser'


def test_edit_post_by_owner(client, new_user, new_post):
    login(client)
    response = client.post(f'/posts/{new_post.id}/edit', data={
        'title': 'Updated Title',
        'summary': '',
        'content': 'Updated content',
        'category': 0,
        'tags': '',
        'published': True,
    }, follow_redirects=True)

    assert response.status_code == 200
    updated = Post.query.get(new_post.id)
    assert updated.title == 'Updated Title'


def test_edit_post_forbidden_for_non_owner(client, app, new_post):
    from app import db
    from app.models import User
    other = User(username='otheruser', email='other@example.com')
    other.set_password('password123')
    db.session.add(other)
    db.session.commit()

    login(client, username='otheruser', password='password123')
    response = client.post(f'/posts/{new_post.id}/edit', data={
        'title': 'Hacked Title',
        'content': 'Hacked content',
        'category': 0,
    })
    assert response.status_code == 403


def test_delete_post_by_owner(client, new_user, new_post):
    login(client)
    post_id = new_post.id
    response = client.post(f'/posts/{post_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert Post.query.get(post_id) is None


def test_search_finds_matching_post(client, new_post):
    response = client.get('/search?q=Test')
    assert response.status_code == 200
    assert new_post.title.encode() in response.data
