import os

os.environ["DATABASE_URL"] = "postgresql:///blogly_test"

from unittest import TestCase

from app import app, db
from models import DEFAULT_IMAGE_URL, User

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        # As you add more models later in the exercise, you'll want to delete
        # all of their records before each test just as we're doing with the
        # User model below.
        User.query.delete()

        self.user_1_first_name = "test1_first"
        self.user_1_last_name = "test1_last"

        test_user = User(
            first_name=self.user_1_first_name,
            last_name=self.user_1_last_name,
            image_url=None,
        )

        self.user_2_first_name = "Max"
        self.user_2_last_name = "Doggo"
        self.user_2_img_url = "https://i.ytimg.com/vi/SfLV8hD7zX4/maxresdefault.jpg"

        dog_user = User(
            first_name=self.user_2_first_name,
            last_name=self.user_2_last_name,
            image_url=self.user_2_img_url,
        )

        db.session.add(test_user)
        db.session.add(dog_user)
        db.session.commit()

        # We can hold onto our test_user's id by attaching it to self (which is
        # accessible throughout this test class). This way, we'll be able to
        # rely on this user in our tests without needing to know the numeric
        # value of their id, since it will change each time our tests are run.
        self.user_1_id = test_user.id
        self.user_2_id = dog_user.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_list_users(self):
        """Should show list of users"""

        with app.test_client() as c:
            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<!-- Test: user-listing.html', html)

            self.assertIn(self.user_1_first_name, html)
            self.assertIn(self.user_1_last_name, html)

    def test_show_new_user_form(self):
        '''Should show form to create a new user'''

        with app.test_client() as c:
            resp = c.get("/users/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<!-- Test: new-user-form.html', html)

    def test_show_user_id_information(self):
        """Should show user details"""

        with app.test_client() as c:
            resp = c.get(f"/users/{self.user_1_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<!-- Test: user-detail.html', html)

            self.assertIn(self.user_1_first_name, html)
            self.assertIn(self.user_1_last_name, html)
            self.assertNotIn("<img", html)

            resp = c.get(f"/users/{self.user_2_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<!-- Test: user-detail.html', html)

            self.assertIn(self.user_2_first_name, html)
            self.assertIn(self.user_2_last_name, html)
            self.assertIn(self.user_2_img_url, html)

    def test_show_user_edit(self):
        '''User edit form should show'''

        with app.test_client() as c:
            resp = c.get(f"/users/{self.user_1_id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<!-- Test: edit-user.html', html)

    def test_submit_user_edit(self):
        """User should be able to edit name and img url"""

        edited_first_name = 'edited first name'
        edited_last_name = 'edited last name'
        edited_img_url = "https://i.ytimg.com/vi/SfLV8hD7zX4/maxresdefault.jpg"

        with app.test_client() as c:
            resp = c.post(
                f"/users/{self.user_1_id}/edit",
                data={
                    'first_name': edited_first_name,
                    'last_name': edited_last_name,
                    'image_url': edited_img_url
                },
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<!-- Test: user-detail.html', html)

            self.assertIn(edited_first_name, html)
            self.assertIn(edited_last_name, html)
            self.assertIn(edited_img_url, html)

    def test_submit_new_user(self):
        """Should be able to create user and redirect to user listings"""

        new_first_name = 'new first name'
        new_last_name = 'new last name'
        new_img_url = "https://i.ytimg.com/vi/SfLV8hD7zX4/maxresdefault.jpg"

        with app.test_client() as c:
            resp = c.post(
                f"/users/new",
                data={
                    'first_name': new_first_name,
                    'last_name': new_last_name,
                    'image_url': new_img_url
                },
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<!-- Test: user-listing.html', html)

            self.assertIn(new_first_name, html)
            self.assertIn(new_last_name, html)

        new_first_empty = ''
        new_last_empty = ''
        new_img_url = ''

        with app.test_client() as c:
            resp = c.post(
                f"/users/new",
                data={
                    'first_name': new_first_empty,
                    'last_name': new_last_empty,
                    'image_url': new_img_url
                },
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Invalid first name.', html)
            self.assertIn('Invalid last name.', html)