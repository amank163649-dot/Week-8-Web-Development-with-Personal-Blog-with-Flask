from flask import redirect, url_for, flash, abort, render_template
from flask_login import login_required, current_user

from app import db
from app.comments import bp
from app.models import Comment


@bp.route('/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'info')
    return redirect(url_for('posts.detail', post_id=post_id))


@bp.route('/moderate')
@login_required
def moderate():
    """Admin-only queue of comments awaiting approval."""
    if not current_user.is_admin:
        abort(403)

    pending = Comment.query.filter_by(approved=False).order_by(Comment.timestamp.desc()).all()
    return render_template('main/moderate.html', title='Moderate Comments', comments=pending)


@bp.route('/<int:comment_id>/approve', methods=['POST'])
@login_required
def approve(comment_id):
    if not current_user.is_admin:
        abort(403)

    comment = Comment.query.get_or_404(comment_id)
    comment.approved = True
    db.session.commit()
    flash('Comment approved.', 'success')
    return redirect(url_for('comments.moderate'))
