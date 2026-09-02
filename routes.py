from flask import render_template, request, flash, redirect, url_for, Response
from app.main import bp
from app.main.forms import ContactForm
from app.models import Post, User, Category


@bp.route('/')
@bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)

    query = Post.query.filter_by(published=True)
    if category_id:
        query = query.filter_by(category_id=category_id)

    posts = query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=5, error_out=False
    )

    categories = Category.query.all()
    stats = {
        'total_posts': Post.query.filter_by(published=True).count(),
        'total_users': User.query.count(),
    }

    return render_template('main/index.html', title='Home', posts=posts,
                            categories=categories, stats=stats)


@bp.route('/search')
def search():
    q = request.args.get('q', '', type=str).strip()
    page = request.args.get('page', 1, type=int)
    posts = None
    if q:
        like = f'%{q}%'
        posts = Post.query.filter(
            Post.published == True,  # noqa: E712
            (Post.title.ilike(like)) | (Post.content.ilike(like))
        ).order_by(Post.timestamp.desc()).paginate(page=page, per_page=5, error_out=False)

    return render_template('main/search.html', title='Search Results', query=q, posts=posts)


@bp.route('/about')
def about():
    return render_template('main/about.html', title='About')


@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # In production this would send an email; here we just acknowledge it.
        flash('Thanks for reaching out! Your message has been received.', 'success')
        return redirect(url_for('main.contact'))

    return render_template('main/contact.html', title='Contact', form=form)


@bp.route('/feed.xml')
def rss_feed():
    posts = Post.query.filter_by(published=True).order_by(Post.timestamp.desc()).limit(20).all()
    xml = render_template('main/feed.xml', posts=posts)
    return Response(xml, mimetype='application/rss+xml')
