"""Blogly application."""

import os

from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, Users

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///blogly')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
print('db:', db)

app.config['SECRET_KEY'] = "SECRET!"
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

@app.get("/")
def list_users():
    """Initial landing page"""

    return redirect("/users")

@app.get("/users")
def show_all_users():
    """List users and show button to add user"""

    users = Users.query.all()
    return render_template(
        'user-listing.html',
        users=users
    )

@app.get("/users/new")
def show_add_form():
    """Show an add form for users"""

    return render_template(
        'new-user-form.html'
    )

@app.get("/users/<int:user_id>")
def show_user_id_information(user_id):
    """Show information about the given user"""

    user = Users.query.get_or_404(user_id)

    return render_template('user-detail.html', user=user)

@app.get("/users/<int:user_id>/edit")
def show_edit_page(user_id):
    """Show the edit page for a user"""

    user = Users.query.get_or_404(user_id)

    return render_template('edit-user.html', user=user)

