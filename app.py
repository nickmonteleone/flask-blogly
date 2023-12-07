"""Blogly application."""

import os

from flask import Flask, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User

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

    users = User.query.all()
    return render_template(
        'user-listing.html',
        users=users
    )

@app.get("/users/new")
def show_new_user_form():
    """Show an add form for users"""

    return render_template(
        'new-user-form.html'
    )

@app.post("/users/new")
def submit_new_user_form():
    """Submit an add form for users"""

    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url']
    )

    name_check = True

    if len(new_user.first_name.strip()) == 0:
        flash(f"Invalid first name.")
        name_check = False

    if len(new_user.last_name.strip()) == 0:
        flash(f"Invalid last name.")
        name_check = False

    if not name_check:
        return redirect('/users')

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")


@app.get("/users/<int:user_id>")
def show_user_id_information(user_id):
    """Show information about the given user"""

    user = User.query.get_or_404(user_id)

    return render_template('user-detail.html', user=user)

@app.get("/users/<int:user_id>/edit")
def show_edit_user_form(user_id):
    """Show the edit page for a user"""

    user = User.query.get_or_404(user_id)

    return render_template('edit-user.html', user=user)

@app.post("/users/<int:user_id>/edit")
def submit_edit_user_form(user_id):
    """Show the edit page for a user"""

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()

    return redirect(f"/users/{user_id}")

@app.post("/users/<int:user_id>/delete")
def delete_user(user_id):
    """Delete the user"""

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect('/users')