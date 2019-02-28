''' Test cases based on the flask documentation. Demonstrates the rough
equivalent of functional tests with a minimalist view which is just a
list of bytes.
'''

from app import create_app, db
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class TestClientExample():
    def setup(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def teardown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_root(self):
        rv = self.client.get('/')
        assert b'New Companies' in rv.data


