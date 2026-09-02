from app.models import Comment
from tests.conftest import login


def test_add_comment_requires_login(client, new_post):
    response = client.post(f'/posts/{new_post.id}', data={'content': 'Nice post'}, follow_redirects=True)
    assert b'Please log in' in response.data or b'Sign In' in response.data


def test_add_comment_success(client, new_user, new_post):
    login(client)
    response = client.post(f'/posts/{new_post.id}', data={
        'content': 'Great article, thanks!',
        'parent_id': '',
    }, follow_redirects=True)

    assert response.status_code == 200
    comment = Comment.query.filter_by(content='Great article, thanks!').first()
    assert comment is not None
    assert comment.post_id == new_post.id


def test_delete_comment_by_author(client, new_user, new_post):
    login(client)
    client.post(f'/posts/{new_post.id}', data={'content': 'Temporary comment', 'parent_id': ''})
    comment = Comment.query.filter_by(content='Temporary comment').first()

    response = client.post(f'/comments/{comment.id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert Comment.query.get(comment.id) is None


def test_nested_reply(client, new_user, new_post):
    login(client)
    client.post(f'/posts/{new_post.id}', data={'content': 'Parent comment', 'parent_id': ''})
    parent = Comment.query.filter_by(content='Parent comment').first()

    client.post(f'/posts/{new_post.id}', data={'content': 'A reply', 'parent_id': str(parent.id)})
    reply = Comment.query.filter_by(content='A reply').first()

    assert reply.parent_id == parent.id
    assert reply in parent.replies
