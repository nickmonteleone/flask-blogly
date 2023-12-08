"""Blogly application."""

import os

from flask import Flask, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, Post, User

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
def index():
    """Initial landing page, redirect to user listing page"""

    return redirect("/users")

##########################################################
# routes for users

@app.get("/users")
def show_all_users():
    """List users on page"""

    users = User.query.all()
    return render_template(
        '/user/listing.html',
        users=users
    )

@app.get("/users/new")
def show_new_user_form():
    """Show an add form for users"""

    return render_template(
        '/user/new-form.html'
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
        flash("Invalid first name.")
        name_check = False

    if len(new_user.last_name.strip()) == 0:
        flash("Invalid last name.")
        name_check = False

    if name_check:
        db.session.add(new_user)
        db.session.commit()
        flash('User successfully added!')


    return redirect("/users")


@app.get("/users/<int:user_id>")
def show_user_id_information(user_id):
    """Show information about the given user"""

    user = User.query.get_or_404(user_id)

    return render_template('/user/detail.html', user=user)
    # TODO: in files, have user files starts w/ "user"


@app.get("/users/<int:user_id>/edit")
def show_edit_user_form(user_id):
    """Show the edit page for a user"""

    user = User.query.get_or_404(user_id)

    return render_template('/user/edit-form.html', user=user)

@app.post("/users/<int:user_id>/edit")
def submit_edit_user_form(user_id):
    """Show the edit page for a user"""

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    input_check = True

    if len(user.first_name.strip()) == 0:
        flash(f"Invalid first name.")
        input_check = False

    if len(user.last_name.strip()) == 0:
        flash(f"Invalid last name.")
        input_check = False
    # TODO: validation method can be in model instead, not route

    if input_check:
        db.session.add(user)
        db.session.commit()
        flash('User successfully edited!')


    return redirect(f"/users/{user_id}")

@app.post("/users/<int:user_id>/delete")
def delete_user(user_id):
    """Delete the user"""

    user = User.query.get_or_404(user_id)

    for post in user.posts:
        db.session.delete(post)

    db.session.delete(user)
    db.session.commit()

    flash('User successfully deleted!')

    return redirect('/users')


##########################################################
# routes for posts

@app.get('/users/<int:user_id>/posts/new')
def show_new_post_form(user_id):
    '''Show page with form to add a new post'''

    user = User.query.get_or_404(user_id)

    return render_template(
        '/post/new-form.html',
        user=user
    )

@app.post('/users/<int:user_id>/posts/new')
def submit_new_post_form(user_id):
    '''Submit form to create a new post'''

    new_post = Post(
        title=request.form['title'],
        content=request.form['content'],
        user_id=user_id
    )

    input_check = True

    if len(new_post.title.strip()) == 0:
        flash(f"Invalid title for post addition.")
        input_check = False

    if len(new_post.content.strip()) == 0:
        flash(f"Invalid content for post addition.")
        input_check = False
    # TODO: move validation elsewhere

    if input_check:
        db.session.add(new_post)
        db.session.commit()
        flash('Post added successfully!')

    return redirect(f'/users/{user_id}')

@app.get('/posts/<int:post_id>')
def show_post_page(post_id):
    '''Show the post page for a particular post'''

    post = Post.query.get_or_404(post_id)

    return render_template(
        '/post/detail.html',
        post=post
    )

@app.get('/posts/<int:post_id>/edit')
def show_edit_post_form(post_id):
    """Show edit post form"""

    post = Post.query.get_or_404(post_id)

    return render_template('/post/edit-form.html', post=post)


@app.post('/posts/<int:post_id>/edit')
def submit_edit_post_form(post_id):
    """Submits edit for post"""

    post = Post.query.get_or_404(post_id)

    post.title = request.form['title']
    post.content = request.form['content']

    input_check = True

    if len(post.title.strip()) == 0:
        flash(f"Invalid edit for post title.")
        input_check = False

    if len(post.content.strip()) == 0:
        flash(f"Invalid edit for post content.")
        input_check = False

    if input_check:
        db.session.add(post)
        db.session.commit()
        flash('Post edited successfully!')

    return redirect(f'/posts/{post_id}')


@app.post("/posts/<int:post_id>/delete")
def delete_post(post_id):
    """Delete post"""

    post = Post.query.get_or_404(post_id)

    user_id = post.user.id

    db.session.delete(post)
    db.session.commit()

    flash('Post deleted successfully!')

    return redirect(f'/users/{user_id}')