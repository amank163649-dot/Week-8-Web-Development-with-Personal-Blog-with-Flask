from app import db
from app.models import User, Post, Comment


def test_password_hashing(app):
    user = User(username='alice', email='alice@example.com')
    user.set_password('mysecret')
    assert user.password_hash != 'mysecret'
    assert user.check_password('mysecret') is True
    assert user.check_password('wrongpassword') is False


def test_new_user_repr(app):
    user = User(username='bob', email='bob@example.com')
    assert repr(user) == '<User bob>'


def test_create_post(app, new_user):
    post = Post(title='Hello World', content='My first post', author=new_user)
    db.session.add(post)
    db.session.commit()

    assert post.id is not None
    assert post.author == new_user
    assert post.published is True


def test_post_comment_relationship(app, new_user, new_post):
    comment = Comment(content='Nice post!', author=new_user, post=new_post)
    db.session.add(comment)
    db.session.commit()

    assert new_post.comments.count() == 1
    assert comment.post == new_post
    assert comment.author == new_user


def test_comment_cascade_delete(app, new_user, new_post):
    comment = Comment(content='Will be deleted', author=new_user, post=new_post)
    db.session.add(comment)
    db.session.commit()
    comment_id = comment.id

    db.session.delete(new_post)
    db.session.commit()

    assert Comment.query.get(comment_id) is None
