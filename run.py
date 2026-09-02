import click
from app import create_app, db
from app.models import User, Post, Comment, Category, Tag

app = create_app()


@app.cli.command('seed')
def seed():
    """Populate the database with sample data for demoing the blog."""
    from datetime import datetime, timedelta

    if User.query.first():
        click.echo('Database already has data. Skipping seed.')
        return

    admin = User(username='admin', email='admin@example.com', is_admin=True,
                 about_me='Site administrator and lead blogger.')
    admin.set_password('admin123')

    jane = User(username='jane', email='jane@example.com',
                about_me='Data enthusiast and Python lover.')
    jane.set_password('jane12345')

    db.session.add_all([admin, jane])

    cat_web = Category(name='Web Development')
    cat_python = Category(name='Python')
    db.session.add_all([cat_web, cat_python])
    db.session.commit()

    post1 = Post(
        title='Getting Started with Flask Web Development',
        summary='Learn how to build your first Flask application with this comprehensive guide.',
        content='<p>In this comprehensive guide, we\'ll explore how to build your first Flask '
                'application, covering routing, templates, and forms.</p>',
        author=admin, category=cat_web,
        timestamp=datetime.utcnow() - timedelta(days=5),
    )
    post2 = Post(
        title='Python Data Analysis with Pandas',
        summary='Explore data analysis techniques using Python\'s pandas library.',
        content='<p>Pandas makes it easy to load, clean, and analyze tabular data in Python.</p>',
        author=jane, category=cat_python,
        timestamp=datetime.utcnow() - timedelta(days=2),
    )
    db.session.add_all([post1, post2])
    db.session.commit()

    c1 = Comment(content='Excellent tutorial! Really helped me understand Flask better.',
                 author=jane, post=post1)
    c2 = Comment(content='Could you add a section about deployment?', author=admin, post=post1)
    db.session.add_all([c1, c2])
    db.session.commit()

    click.echo('Database seeded with sample users, posts, and comments.')
    click.echo('Login as admin / admin123 or jane / jane12345')


if __name__ == '__main__':
    app.run(debug=True)
