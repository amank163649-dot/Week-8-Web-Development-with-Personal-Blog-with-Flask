# Personal Blog with Flask

A full-featured personal blog website built with Flask, featuring user authentication,
blog post management, a commenting system, and a responsive Bootstrap design. This
project demonstrates complete web development skills with Python: routing, templating,
form handling, database modeling, and application architecture.

---

## Project Description

This blog lets registered users write, edit, and delete their own posts; readers can
browse, search, and comment on posts (including threaded replies); and an admin account
can moderate comments before they go public. The app is structured using Flask's
**application factory** pattern and **blueprints**, so authentication, posts, comments,
and general pages are cleanly separated into their own modules.

**Goals of this project:**
- Practice building a real, multi-page Flask application (not just a single-file script)
- Model relational data (users, posts, comments, categories, tags) with SQLAlchemy
- Implement secure authentication from scratch with password hashing and sessions
- Handle forms, validation, and file uploads safely
- Build a responsive, good-looking UI with Jinja2 templates and Bootstrap 5

---

## What I Learned

- **Flask Framework** — application factory pattern, blueprints, url routing, error handlers
- **Database Integration** — SQLAlchemy ORM with SQLite, one-to-many and many-to-many
  relationships, cascading deletes, self-referential relationships (comment replies)
- **User Authentication** — secure login/registration with Flask-Login, session
  management, protected routes with `@login_required`, ownership checks (403 vs 404)
- **Template Engine** — Jinja2 template inheritance, macros for reusable UI (post cards,
  pagination, recursive comment rendering), template context processors
- **Form Handling** — Flask-WTF forms, server-side validation, CSRF protection, file
  upload validation
- **Web Security** — password hashing with Werkzeug, CSRF tokens on every form,
  authorization checks so users can only edit/delete their own content
- **Responsive Design** — mobile-friendly layout with Bootstrap 5's grid and components

---

## Features

- ✅ User registration and authentication (login/logout, password hashing)
- ✅ User profiles with bio and list of authored posts
- ✅ Create, read, update, delete (CRUD) blog posts
- ✅ Comment system with **threaded replies** and admin **moderation queue**
- ✅ Simple rich-text formatting toolbar for post creation (bold/italic/link/heading/quote)
- ✅ Full-text search across post titles and content
- ✅ Pagination for post lists, profile pages, and search results
- ✅ Responsive Bootstrap 5 design (mobile-friendly navbar, cards, forms)
- ✅ Cover image upload support for posts
- ✅ Categories and comma-separated tags for organizing posts
- ✅ Social sharing buttons (Twitter/X, Facebook, LinkedIn)
- ✅ RSS feed (`/feed.xml`) of the latest posts
- ✅ Contact form
- ✅ Custom 404 / 500 error pages
- ✅ Automated test suite (models, auth, posts, comments)

---

## Technical Architecture

### Project Structure

```
week8-flask-blog/
│── app/
│   ├── __init__.py          # Application factory, extension setup, error handlers
│   ├── models.py             # User, Post, Comment, Category, Tag models
│   ├── auth/                 # Registration, login, logout, profile blueprint
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── main/                 # Home page, search, about, contact, RSS blueprint
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── posts/                 # Post CRUD blueprint
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── comments/              # Comment create/delete/moderate blueprint
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/main.js
│   │   └── images/uploads/    # User-uploaded post images
│   └── templates/
│       ├── base.html          # Base layout: navbar, flash messages, footer
│       ├── _post_card.html    # Reusable post-summary card macro
│       ├── _pagination.html   # Reusable pagination macro
│       ├── auth/               # register, login, profile, edit_profile
│       ├── main/               # index, search, about, contact, moderate, feed.xml
│       ├── posts/              # list, detail, create_edit
│       └── errors/             # 404, 500
│── migrations/                 # Flask-Migrate (Alembic) migration scripts
│── tests/                      # Pytest suite
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_auth.py
│   ├── test_posts.py
│   └── test_comments.py
│── config.py                   # App configuration (env-driven)
│── requirements.txt
│── run.py                      # Entry point + `flask seed` CLI command
│── README.md
└── .gitignore
```

### Data Model

- **User** `1 ── * ` **Post** (a user authors many posts)
- **User** `1 ── *` **Comment** (a user writes many comments)
- **Post** `1 ── *` **Comment** (a post has many comments)
- **Post** `* ── *` **Tag** (via the `post_tags` association table)
- **Category** `1 ── *` **Post** (a category groups many posts)
- **Comment** `1 ── *` **Comment** — self-referential `parent_id` foreign key enables
  threaded replies; deleting a comment cascades to delete its replies.

Deleting a `User` cascades to delete their `Post`s and `Comment`s. Deleting a `Post`
cascades to delete its `Comment`s. This is implemented with SQLAlchemy's
`cascade='all, delete-orphan'` on the relevant relationships.

### Key Design Decisions

- **Application factory (`create_app`)** instead of a global `app` object, so the app can
  be configured differently for testing (in-memory SQLite, CSRF disabled) vs. production.
- **Blueprints** keep each feature area (auth/main/posts/comments) self-contained with its
  own routes and forms, mirroring how a larger Flask codebase would be organized.
- **Ownership checks** (`current_user.id == post.user_id`) return `403 Forbidden` rather
  than silently redirecting, so users get a clear signal they don't own that resource.
  `is_admin` users can bypass ownership checks to moderate any content.
- **Dynamic relationships** (`lazy='dynamic'`) on `posts`/`comments` let routes chain
  `.filter_by()`, `.order_by()`, and `.paginate()` directly on the relationship instead of
  loading the whole collection into memory first.
- **CSRF protection** is enabled globally via `CSRFProtect`; every form includes
  `{{ form.hidden_tag() }}` to render the CSRF token.

---

## How to Run

### 1. Install dependencies

```bash
# (Recommended) create and activate a virtual environment first
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and adjust as needed (a working default is provided, so
this step is optional for local development):

```bash
cp .env.example .env
```

### 3. Initialize the database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

> If you'd rather skip migrations for a quick local run, `db.create_all()` is also
> triggered automatically the first time you run the seed command below against a fresh
> `instance/blog.db`.

### 4. (Optional) Seed sample data

Populates the database with two demo users, sample posts, and comments so the blog isn't
empty on first run:

```bash
flask seed
```

This creates:
- `admin` / `admin123` (admin account, can moderate comments)
- `jane` / `jane12345`

### 5. Run the application

```bash
python run.py
```

Visit **http://localhost:5000** in your browser.

### 6. Run the tests

```bash
pytest
```

---

## Required Libraries

| Library | Purpose |
|---|---|
| Flask | Web framework |
| Flask-SQLAlchemy | Database ORM |
| Flask-WTF | Form handling & CSRF protection |
| Flask-Login | User session management |
| Flask-Migrate | Database migrations (Alembic) |
| Bootstrap-Flask | Bootstrap 5 integration helpers |
| WTForms | Form field types & validators |
| Werkzeug | Password hashing & WSGI utilities |
| email-validator | Email format validation for WTForms |
| python-dotenv | Loads `.env` file for local config |
| pytest | Test runner |

---

## Testing Evidence

The `tests/` directory contains automated tests covering the core user flows, run
against an in-memory SQLite database so they don't touch your real data:

- **`test_models.py`** — password hashing correctness, model creation, relationships,
  cascading deletes (deleting a post deletes its comments)
- **`test_auth.py`** — registration (success + duplicate username rejection), login
  (success + wrong password), logout, protected-route redirect when logged out
- **`test_posts.py`** — home page loads, post detail view + view counter, 404 on missing
  post, create/edit/delete require login, edit/delete return 403 for non-owners, search
  returns matching posts
- **`test_comments.py`** — commenting requires login, comment creation, comment deletion
  by its author, threaded replies (`parent_id` linkage)

Run them with:

```bash
pytest -v
```

Example of what a passing run looks like:

```
tests/test_auth.py::test_register_page_loads PASSED
tests/test_auth.py::test_register_new_user PASSED
tests/test_auth.py::test_login_success PASSED
tests/test_comments.py::test_add_comment_success PASSED
tests/test_comments.py::test_nested_reply PASSED
tests/test_posts.py::test_edit_post_forbidden_for_non_owner PASSED
tests/test_models.py::test_comment_cascade_delete PASSED
...
```

---

## Deployment Notes

This app is ready to deploy to a platform like **PythonAnywhere**, **Render**, or
**Heroku**:

1. Set `SECRET_KEY` and `DATABASE_URL` as environment variables on the host (don't rely
   on the fallback dev values in `config.py`).
2. Use a production database (e.g., a hosted Postgres instance) via `DATABASE_URL`
   rather than SQLite for anything beyond a demo.
3. Run `flask db upgrade` on the host to apply migrations.
4. Serve with a production WSGI server (e.g., `gunicorn run:app`) instead of the Flask
   dev server (`python run.py`).
5. Ensure `app/static/images/uploads/` is writable, or point `UPLOAD_FOLDER` at
   persistent storage if the platform's filesystem is ephemeral.

---

## Screenshots

_Screenshots of the running application (home page, post detail with comments, login,
and post editor) should be added here before final submission — run the app locally per
the steps above and capture each page._

---

© 2026 My Personal Blog — Built with Flask for learning purposes.
