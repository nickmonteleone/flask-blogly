import os

os.environ["DATABASE_URL"] = "postgresql:///blogly_test"

from unittest import TestCase

from app import app, db
from models import Post, User
# from models import  DEFAULT_IMAGE_URL


# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

class PostsTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        # Clear tables and make sure there is test user with test post
        Post.query.delete()
        User.query.delete()

        test_user = User(
            first_name='test',
            last_name='test',
            image_url=None,
        )

        db.session.add(test_user)
        db.session.commit()

        self.user_id = test_user.id
        self.user_first_name = test_user.first_name
        self.user_last_name = test_user.last_name

        self.test_post_title = 'Test Post'
        self.test_post_content = 'Test Test Test Test Test Test Test Test Test '

        test_post = Post(
            title=self.test_post_title,
            content=self.test_post_content,
            user_id=self.user_id
        )

        db.session.add(test_post)
        db.session.commit()

        self.test_post_id = test_post.id

        self.new_post_title = 'new post test'
        self.new_post_content = 'new new new new new new new new new new new new!'

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_show_new_post_form(self):
        '''Should open form to add a new post'''

        with app.test_client() as c:
            resp = c.get(f"/users/{self.user_id}/posts/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<!-- Test: new-post-form.html', html)

    def test_submit_new_post_form(self):
        '''Should create post upon form submit'''

        with app.test_client() as c:
            resp = c.post(
                f"/users/{self.user_id}/posts/new",
                data={
                    'title': self.new_post_title,
                    'content': self.new_post_content
                },
                follow_redirects=True)
            html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<!-- Test: user-detail.html', html)

        self.assertIn(self.new_post_title, html)

    def test_show_post_page(self):
        '''Should show details for a post on post page'''

        with app.test_client() as c:
            resp = c.get(f"/posts/{self.test_post_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<!-- Test: post-detail.html', html)

            self.assertIn(self.test_post_title, html)
            self.assertIn(self.test_post_content, html)
            self.assertIn(self.user_first_name, html)
            self.assertIn(self.user_last_name, html)

            resp = c.get(f"/posts/99999999999")
            self.assertEqual(resp.status_code, 404)

    def test_show_edit_post_form(self):
        '''Should show details for a post on post page'''

        with app.test_client() as c:
            resp = c.get(f"/posts/{self.test_post_id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<!-- Test: edit-post.html', html)

            self.assertIn(self.test_post_title, html)
            self.assertIn(self.test_post_content, html)

            resp = c.get(f"/posts/99999999999")
            self.assertEqual(resp.status_code, 404)

    def test_submit_edit_post_form(self):
        '''Should create post upon form submit'''

        edited_title = 'test new title for edit'
        edited_content = 'afsdhfalsudryaweiouryhhkasf'

        with app.test_client() as c:
            resp = c.post(
                f"/posts/{self.test_post_id}/edit",
                data={
                    'title': edited_title,
                    'content': edited_content
                },
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<!-- Test: post-detail.html', html)

            self.assertIn(edited_title, html)
            self.assertIn(edited_content, html)
            self.assertIn(self.user_first_name, html)
            self.assertIn(self.user_last_name, html)

            resp = c.post("/posts/9999999999/edit")
            self.assertEqual(resp.status_code, 404)

    def test_delete_post(self):
        '''Should be able to delete a post'''

        with app.test_client() as c:
            resp = c.post(
                f"/posts/{self.test_post_id}/delete",
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<!-- Test: user-detail.html', html)

            self.assertNotIn(self.test_post_title, html)

            resp = c.post("/posts/9999999999/delete")
            self.assertEqual(resp.status_code, 404)

