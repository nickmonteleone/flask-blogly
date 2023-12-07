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

        test_user = User(
            first_name="test1_first",
            last_name="test1_last",
            image_url=None,
        )

        dog_user = User(
            first_name="Max",
            last_name="Doggo",
            image_url='https://i.ytimg.com/vi/SfLV8hD7zX4/maxresdefault.jpg',
        )

        db.session.add(test_user)
        db.session.add(dog_user)
        db.session.commit()

        # We can hold onto our test_user's id by attaching it to self (which is
        # accessible throughout this test class). This way, we'll be able to
        # rely on this user in our tests without needing to know the numeric
        # value of their id, since it will change each time our tests are run.
        self.user_id = test_user.id
        self.user_id2 = dog_user.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_list_users(self):
        with app.test_client() as c:
            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("test1_first", html)
            self.assertIn("test1_last", html)

    def test_show_new_user_form(self):
        with app.test_client() as c:
            resp = c.get("/users/new")
            html = resp.get_data(as_text=True)
            self.assertIn('<!-- Test: new-user-form.html', html)

    def test_show_user_id_information(self):
        with app.test_client() as c:
            resp = c.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)
            self.assertIn("test1_first", html)
            self.assertIn("test1_last", html)
            self.assertNotIn("<img", html)

            resp = c.get(f"/users/{self.user_id2}")
            html = resp.get_data(as_text=True)
            self.assertIn("Max", html)
            self.assertIn("Doggo", html)
            self.assertIn("https://i.ytimg", html)

