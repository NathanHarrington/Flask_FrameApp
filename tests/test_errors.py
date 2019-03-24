''' Bare bones testing of bytes returned in a response payload. Designed
to bridge the gap between unit tests and functional tests.
'''
import os, shutil
from app import create_app, db
from config import Config

class TestConfigForServerError(Config):
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class TestErrorsAndLogs(Config):
    def setup(self):
        # Remove the log folder for coverage
        if os.path.exists('logs'):
            # But not on Windows, as that throws a file in use error
            if not sys.platform.startswith('win'):
                shutil.rmtree('logs')

        self.app = create_app(TestConfigForServerError)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def teardown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_error_404(self):
        pfx = 'http://localhost:5000/labborked'
        rv = self.client.get(pfx)
        assert rv.status_code == 404

    def test_error_500(self):
        pfx = 'http://localhost:5000/fail'
        rv = self.client.get(pfx)
        assert rv.status_code == 500
