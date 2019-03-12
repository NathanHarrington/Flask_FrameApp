''' Test cases based on the flask documentation. Demonstrates the rough
equivalent of functional tests with a minimalist view which is just a
list of bytes.
'''
from flask import url_for
from app import create_app, db
from app.models import User, Post, Crawled
from config import Config
import random

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False

class TestFunctionalExamples():
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

    def test_basic_home(self):
        # Martin has heard about a cool new online listing of companies
        # He goes to check out its homepage
        url = 'http://localhost:5000/index'
        rv = self.client.get(url)

        # He notices the page title and header mention companies
        assert b'Companies\n</title>' in rv.data
        assert b'<h1>New Companies' in rv.data


    def test_new_sign_up(self):
        # Martin liked what he saw on the home page, so he went back to
        # home and decided to login
        rv = self.client.get('/')

        # He sees the 'login' link, clicks it
        assert b'/auth/login' in rv.data
        rv = self.client.get('/auth/login')

        # He seees the 'click to register' link and follows it
        assert b'Click to Register!' in rv.data
        rv = self.client.get('/auth/register')

        # He sees details of the register form
        assert b'Repeat Password' in rv.data

        form_data = {'username': 'martin',
                     'email': 'martin@example.com',
                     'password': 'martin', 'password2': 'martin' }
        rv = self.client.post('/auth/register', data=form_data,
                              follow_redirects=True)

        # Martin sees the flash message about a new id, and he's now on
        # the login page
        assert b'Congratulations, you are now' in rv.data

    def show(self, response):
        ''' Helper function to print better formatted html text to
        stdout.
        '''
        str_data = str(response.data)
        str_data = str_data.replace('\\n', '\n')
        str_data = str_data.replace('\\t', '  ')
        print(str_data)

    def load_example_user(self):
        ''' App context is already established, so connect to the db
        directly and add the test user. '''
        muser = User(username='martin', email='martin@example.com)')
        muser.set_password('martin')
        assert muser.check_password('dog') == False
        assert muser.check_password('martin') == True
        db.session.add(muser)
        db.session.commit()

        self.load_example_posts(muser, total_posts=10)

    def load_example_posts(self, new_user, total_posts=10):
        ''' App context is already established, so connect to the db
        directly and add a variety of example posts. '''
        post_words = ['In', 'the', 'story', 'there', 'was', 'stuff']
        for post_item in range(total_posts):
            random.shuffle(post_words)
            body = ' '.join(post_words)
            body += ' Post number: %s' % post_item

            # Walk through each user, add N posts
            post = Post(body=body, author=new_user)
            db.session.add(post)

        db.session.commit()

    def load_example_companies(self, total_companies=20):
        ''' App context is already established, so connect to the db
        directly and add some test companies based on random dictionary
        values. 
        '''

        comp = {
            'ein_number': ['12345'],
            'company_type': ['Retail', 'Landscaping'],
            'certificate_type': ['LLC', 'S-CORP'],
            'company_name': ['MyBusiness', 'Cupcakes', 'Grass Cutters'],
            'street_address': ['123 main street', '456 elm street'],
            'city': ['Holly Springs', 'Cary', 'Apex', 'Raleigh'],
            'state': ['NC', 'VA', 'MS', 'UT'],
            'zip_code': ['27540', '27513', '27709', '84321']
            }
        for comp_item in range(total_companies):
            ri = random.randint
            rnd_number = random.randint(0,12345)
            newc = Crawled(ein_number=rnd_number,
                 company_type=comp['company_type'][ri(0,1)],
                 certificate_type=comp['certificate_type'][ri(0,1)],
                 company_name=comp['company_name'][ri(0,2)],
                 street_address=comp['street_address'][ri(0,1)],
                 city=comp['city'][ri(0,3)],
                 state=comp['state'][ri(0,3)],
                 zip_code=comp['zip_code'][ri(0,3)]
                )
            db.session.add(newc)

        db.session.commit()

    def test_login(self):
        self.load_example_user()
        # Martin has run through the registration process, and now he
        # wants to login
        rv = self.client.get('/')
        assert b'/auth/login' in rv.data

        # He enters his authentication details, clicks submit
        form_data = {'username': 'martin', 'password': 'martin'}
        rv = self.client.post('/auth/login', data=form_data,
                              follow_redirects=True)

        # He sees the home page now says 'Edit Profile'
        assert b'Edit Profile' in rv.data

    def test_exploring(self):
        self.load_example_user()
        # Martin logs in, clicks explore at the top
        form_data = {'username': 'martin', 'password': 'martin'}
        rv = self.client.post('/auth/login', data=form_data,
                              follow_redirects=True)
        assert b'Edit Profile' in rv.data
        assert b'/explore' in rv.data

        # He clicks explore, sees the new posts on the explore screen
        rv = self.client.get('/explore')
        exp_str = b'said <span class="flask-moment" data-timestamp'
        assert exp_str in rv.data

        # He clicks one of the user list, looks at the users profile,
        # sees they have pages of posts
        rv = self.client.get('/user/martin')
        assert b'Last seen on:' in rv.data

        # Clicks 'older posts' to see more content
        rv = self.client.get('/user/martin?page=2')
        assert b'Post number: 1' in rv.data

    def test_not_signed_in_no_explore(self):
        # Martin moves his bookmarks, and tries to go right to explore
        # on a new computer without logging in first:
        self.load_example_user()

        # He tries to go to explore first, should not see the explore
        # link, does see the 'you must login page'
        rv = self.client.get('/explore')
        assert b'/explore' not in rv.data
        assert b'/auth/login' in rv.data

        # Martin logs in, clicks explore at the top
        form_data = {'username': 'martin', 'password': 'martin'}
        rv = self.client.post('/auth/login', data=form_data,
                              follow_redirects=True)
        assert b'/explore' in rv.data

    def test_username_taken(self):
        # Martin has already signed up, forgets and tries again with the
        # same username

        # First sign up is successful
        form_data = {'username': 'martin',
                     'email': 'martin@example.com',
                     'password': 'martin', 'password2': 'martin' }
        rv = self.client.post('/auth/register', data=form_data,
                              follow_redirects=True)
        assert b'Congratulations, you are now' in rv.data

        # On second submit, he sees the flash message about the problem
        rv = self.client.post('/auth/register', data=form_data,
                              follow_redirects=True)
        assert b'Congratulations, you are now' not in rv.data
        assert b'Please use a different username' in rv.data

    def test_email_taken(self):
        # Martin has already signed up, forgets and tries again with a
        # different username but the same email

        # First sign up is successful
        form_data = {'username': 'newmartin',
                     'email': 'martin@example.com',
                     'password': 'martin', 'password2': 'martin' }
        rv = self.client.post('/auth/register', data=form_data,
                              follow_redirects=True)
        assert b'Congratulations, you are now' in rv.data

        # On second submit, he sees the flash message about the problem
        rv = self.client.post('/auth/register', data=form_data,
                              follow_redirects=True)
        assert b'Congratulations, you are now' not in rv.data
        assert b'Please use a different email' in rv.data

    def test_login_invalid_username_password_shows_feedback(self):
        self.load_example_user()

        # Martin uses the wrong username to login
        form_data = {'username': 'martin_oops', 'password': 'martin'}
        rv = self.client.post('/auth/login', data=form_data,
                              follow_redirects=True)
        assert b'Edit Profile' not in rv.data
        assert b'Invalid username or password' in rv.data

        # Martin uses the wrong username to login
        form_data = {'username': 'martin', 'password': 'martin_oops'}
        rv = self.client.post('/auth/login', data=form_data,
                              follow_redirects=True)
        assert b'Edit Profile' not in rv.data
        assert b'Invalid username or password' in rv.data

    def test_login_twice_goes_back_to_index(self):
        # Martin logs in
        self.load_example_user()
        form_data = {'username': 'martin', 'password': 'martin'}
        rv = self.client.post('/auth/login', data=form_data,
                              follow_redirects=True)
        assert b'Edit Profile' in rv.data

        # Hits back button, then tries to go to /login again without
        # submitting the form
        rv = self.client.get('/auth/login', follow_redirects=True)

        # Which redirects him to the main index because he is already
        # logged in
        # He notices the page title and header mention companies
        assert b'Companies\n</title>' in rv.data
        assert b'<h1>New Companies' in rv.data

    def test_register_after_login_goes_back_to_index(self):
        # Martin logs in
        self.load_example_user()
        form_data = {'username': 'martin', 'password': 'martin'}
        rv = self.client.post('/auth/login', data=form_data,
                              follow_redirects=True)
        assert b'Edit Profile' in rv.data

        # Hits back button, then tries to go to /register again without
        # submitting the form
        rv = self.client.get('/auth/register', follow_redirects=True)

        # Which redirects him to the main index because he is already
        # logged in
        # He notices the page title and header mention companies
        assert b'Companies\n</title>' in rv.data
        assert b'<h1>New Companies' in rv.data

    def test_reset_password_after_login_goes_to_index(self):
        # Martin logs in, then goes to the 'reset password' link
        # directly
        self.load_example_user()
        form_data = {'username': 'martin', 'password': 'martin'}
        rv = self.client.post('/auth/login', data=form_data,
                              follow_redirects=True)
        assert b'Edit Profile' in rv.data

        rv = self.client.get('/auth/reset_password_request',
                             follow_redirects=True)
        # He sees that he's back on the main index with edit profile
        # visible
        assert b'Companies\n</title>' in rv.data
        assert b'<h1>New Companies' in rv.data
        assert b'Edit Profile' in rv.data

    def test_reset_password_displays_feedback(self):
        # Martin tries to login, fails
        self.load_example_user()
        form_data = {'username': 'martin', 'password': 'forgot'}
        rv = self.client.post('/auth/login', data=form_data,
                              follow_redirects=True)
        assert b'Edit Profile' not in rv.data

        # Sees the reset password link, follows it
        self.show(rv)
        assert b'href="/auth/reset_password_request">' in rv.data
        rv = self.client.get('/auth/reset_password_request')

        form_data = {'email': 'martin@example.com'}
        rv = self.client.post('/auth/reset_password_request',
                              data=form_data, follow_redirects=True)
        msg = b'Check your email for the instructions to reset your'
        assert msg in rv.data

    def test_logout_goes_back_to_index(self):
        # Martin logs in
        self.load_example_user()
        form_data = {'username': 'martin', 'password': 'martin'}
        rv = self.client.post('/auth/login', data=form_data,
                              follow_redirects=True)
        assert b'Edit Profile' in rv.data

        # Clicks the logout button, verifies he cannot see his profile,
        # and is back at the main index
        rv = self.client.get('/auth/logout', follow_redirects=True)

        assert b'Edit Profile' not in rv.data
        assert b'Companies\n</title>' in rv.data
        assert b'<h1>New Companies' in rv.data

    def test_revisit_of_a_password_reset_link(self):
        # Martin logs in
        self.load_example_user()
        form_data = {'username': 'martin', 'password': 'martin'}
        rv = self.client.post('/auth/login', data=form_data,
                              follow_redirects=True)

        # He finds an old tab left open with a password reset link, he
        # follows it
        prlink = '/auth/reset_password/reset_token_goes_here'
        rv = self.client.get(prlink, follow_redirects=True)

        # Gets redirected to home because he is already logged in
        assert b'Edit Profile' in rv.data
        assert b'Companies\n</title>' in rv.data
        assert b'<h1>New Companies' in rv.data



    def test_user_back_to_explore(self):
        self.load_example_user()
        self.load_example_companies()
        # Martin has bookmarked a specific user, now he comes back
        # there, then clicks explore
        form_data = {'username': 'martin', 'password': 'martin'}
        rv = self.client.post('/auth/login', data=form_data,
                              follow_redirects=True)
        assert b'/explore' in rv.data

        # sees the explore link at the top, follows it
        assert b'/explore' in rv.data
        rv = self.client.get('/explore')

        # Sees the companies list
        assert b'20 total companies' in rv.data

        # Clicks the entire companies list
        rv = self.client.get('/companies')
        assert b'Companies created this week' in rv.data

        # Pages through some results
        rv = self.client.get('/companies?page=2')
        assert b'Page 2 of 4' in rv.data

    def martin_login(self):
        ''' Convenience function to login the martin user. '''
        form_data = {'username': 'martin', 'password': 'martin'}
        rv = self.client.post('/auth/login', data=form_data,
                              follow_redirects=True)

    def test_user_can_post(self):
        self.load_example_user()
        self.load_example_companies()
        self.martin_login()

        # User looks at their profile, notices the 'New Post' button
        rv = self.client.get('/edit_profile')
        assert b'New Post' in rv.data

        # Follows the link, fills out the form, submits it
        rv = self.client.get('/my_posts')
        assert b'Say something' in rv.data
        form_data = {'post': 'Simulated post from tester' }
        rv = self.client.post('/my_posts', data=form_data,
                              follow_redirects=True)

        # Sees their new post on the 'my posts' page
        assert b'Simulated post from tester' in rv.data

        # Clicks explore, sees their post at the top of the list
        rv = self.client.get('/explore')
        assert b'Simulated post from tester' in rv.data
