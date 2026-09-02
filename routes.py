import os
import uuid
from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user

from app import db
from app.posts import bp
from app.posts.forms import PostForm
from app.comments.forms import CommentForm
from app.models import Post, Category, Tag, Comment


def save_image(file_storage):
    """Save an uploaded image with a unique filename and return the filename."""
    ext = file_storage.filename.rsplit('.', 1)[-1].lower()
    filename = f'{uuid.uuid4().hex}.{ext}'
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file_storage.save(path)
    return filename


def process_tags(tag_string):
    """Turn a comma-separated string into a list of Tag objects, creating new ones as needed."""
    tags = []
    if not tag_string:
        return tags
    names = {name.strip() for name in tag_string.split(',') if name.strip()}
    for name in names:
        tag = Tag.query.filter_by(name=name).first()
        if tag is None:
            tag = Tag(name=name)
            db.session.add(tag)
        tags.append(tag)
    return tags


@bp.route('/')
def list_posts():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(published=True).order_by(Post.timestamp.desc()) \
        .paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    return render_template('posts/list.html', title='All Posts', posts=posts)


@bp.route('/<int:post_id>', methods=['GET', 'POST'])
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    if not post.published and (not current_user.is_authenticated or current_user.id != post.user_id):
        abort(404)

    # Increment the view counter (simple, no dedup logic for this project's scope)
    post.views = (post.views or 0) + 1
    db.session.commit()

    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Please log in to comment.', 'info')
            return redirect(url_for('auth.login', next=request.url))

        parent_id = int(comment_form.parent_id.data) if comment_form.parent_id.data else None
        comment = Comment(
            content=comment_form.content.data,
            author=current_user,
            post=post,
            parent_id=parent_id,
            approved=True,
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted.', 'success')
        return redirect(url_for('posts.detail', post_id=post.id))

    top_level_comments = post.comments.filter_by(parent_id=None, approved=True) \
        .order_by(Comment.timestamp.asc()).all()

    return render_template('posts/detail.html', title=post.title, post=post,
                            comments=top_level_comments, comment_form=comment_form)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()
    form.category.choices = [(0, 'Uncategorized')] + \
        [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]

    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            summary=form.summary.data,
            content=form.content.data,
            published=form.published.data,
            author=current_user,
        )
        if form.category.data and form.category.data != 0:
            post.category_id = form.category.data

        if form.image.data:
            post.image_filename = save_image(form.image.data)

        post.tags = process_tags(form.tags.data)

        db.session.add(post)
        db.session.commit()
        flash('Your post has been published!', 'success')
        return redirect(url_for('posts.detail', post_id=post.id))

    return render_template('posts/create_edit.html', title='New Post', form=form, post=None)


@bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    form = PostForm(obj=post)
    form.category.choices = [(0, 'Uncategorized')] + \
        [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]

    if request.method == 'GET':
        form.category.data = post.category_id or 0
        form.tags.data = ', '.join(tag.name for tag in post.tags)

    if form.validate_on_submit():
        post.title = form.title.data
        post.summary = form.summary.data
        post.content = form.content.data
        post.published = form.published.data
        post.category_id = form.category.data if form.category.data != 0 else None
        post.tags = process_tags(form.tags.data)

        if form.image.data:
            post.image_filename = save_image(form.image.data)

        db.session.commit()
        flash('Your post has been updated.', 'success')
        return redirect(url_for('posts.detail', post_id=post.id))

    return render_template('posts/create_edit.html', title='Edit Post', form=form, post=post)


@bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.', 'info')
    return redirect(url_for('main.index'))
