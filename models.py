"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

DEFAULT_IMAGE_URL = 'https://upload.wikimedia.org/wikipedia/commons/d/d9/Collage_of_Nine_Dogs.jpg'

def connect_db(app):
    """Connect to database."""

    app.app_context().push()
    db.app = app
    db.init_app(app)

class User(db.Model):
    """Users table."""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True)

    first_name = db.Column(
        db.String(50),
        nullable=False)

    last_name = db.Column(
        db.String(50),
        nullable=False)
    # TODO: for adding default, need to have nullable false
    image_url = db.Column(
        db.String(100))

    posts = db.relationship("Post", backref='user')


class Post(db.Model):
    """Posts table"""

    __tablename__ = "posts"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True)

    title = db.Column(
        db.String(50),
        nullable=False)

    content = db.Column(
        db.Text,
        nullable=False)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now()
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )