''' Functional tests only for the FrameApp flask demonstration
application.

Make sure you export scripts/gecokdriver into PATH
'''

from splinter import Browser
from flask_testing import LiveServerTestCase
from app import create_app, db
from app.models import User, Post, Crawled
from config import Config
import random, time

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class TestTemporaryBase(LiveServerTestCase):
    def create_app(self):
        ''' Required by the flask testing interface, different from the
        flask-wide create_app. '''
        app = create_app(TestConfig)
        app_context = app.app_context()
        app_context.push()
        db.create_all()

        self.load_example_user()
        self.load_example_companies()

        return app

    def setUp(self):
        ''' Create a new database on every test case. '''
        db.session.commit()
        db.drop_all()
        db.create_all()
        self.browser = Browser()

    def tearDown(self):
        ''' Destroy all temporary database data. '''
        self.browser.quit()
        db.session.remove()
        db.drop_all()
        # Where does this belong? What if you run multiple tests?
        #app.app_context.pop()

    def test_basic_home(self):
        # Martin has heard about a cool new online listing of companies He goes to check out its homepage
        url = 'http://localhost:5000'
        self.browser.visit(url)

        # He notices the page title and header mention companies
        assert 'Companies' in self.browser.title
        header = self.browser.find_by_tag('li')[2]
        assert 'Companies' in header.text

    def test_sign_up(self):
        # Martin liked what he saw in basic test, so he went back to
        # home and decided to login
        url = 'http://localhost:5000'
        self.browser.visit(url)

        # He clicks the 'login' link
        sbfl = self.browser.find_link_by_href
        login_links = sbfl('/auth/login')
        login_links[0].click()

        # He sees the 'click to register' link and follows it
        fnd_txt = self.browser.is_text_present('Click to Register!')
        assert fnd_txt == True

        reg_links = sbfl('/auth/register')
        reg_links[0].click()

        fnd_txt = self.browser.is_text_present('Repeat Password')
        assert fnd_txt == True

        # He creates an id, clicks submit
        self.browser.fill('username', 'martin')
        self.browser.fill('email', 'martin@example.com')
        self.browser.fill('password', 'martin')
        self.browser.fill('password2', 'martin')
        self.browser.find_by_name('submit').first.click()

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
        # Martin has run through the registration process, and now he
        # wants to login
        url = 'http://localhost:5000'
        br = self.browser
        br.visit(url)
        
        sbfl = self.browser.find_link_by_href
        login_link = sbfl('/auth/login')[0]
        login_link.click()

        # He enters his authentication details, clicks submit
        br.fill('username', 'martin')
        br.fill('password', 'martin')
        self.browser.find_by_name('submit').first.click()

        # He sees the home page now says 'Edit Profile'
        fnd_txt = self.browser.is_text_present('Edit Profile')
        assert fnd_txt == True

    def test_exploring(self):
        # Martin logs in, clicks explore at the top
        url = 'http://localhost:5000/auth/login'
        br = self.browser
        br.visit(url)
        br.fill('username', 'martin')
        br.fill('password', 'martin')
        self.browser.find_by_name('submit').first.click()

        # He clicks explore, sees the new posts on the explore screen
        br.visit('http://localhost:5000/explore')
        itp = self.browser.is_text_present
        assert itp('said a few seconds ago') == True

        # He clicks one of the user list, looks at the users profile,
        # sees they have pages of posts
        user_links = self.browser.find_link_by_href('/user/martin')
        user_links[0].click()
        assert itp('Last seen on:') == True

        # Clicks 'older posts' to see more content
        flbh = self.browser.find_link_by_href
        flbh('/user/martin?page=2').click()
        assert itp('Post number: 1') == True

    def test_user_back_to_explore(self):
        # Martin has bookmarked a specific user, now he comes back
        # there, then clicks explore
        url = 'http://localhost:5000/auth/login'
        self.browser.visit(url)
        self.browser.fill('username', 'martin')
        self.browser.fill('password', 'martin')
        self.browser.find_by_name('submit').first.click()

        # Starts at user martin
        url = 'http://localhost:5000/user/martin'
        self.browser.visit(url)

        # sees the explore link at the top
        exp_link = self.browser.find_link_by_href('/explore')
        exp_link.click()

        # Clicks it, sees the companies list
        itp = self.browser.is_text_present
        assert itp('20 total companies') == True

        # Clicks the entire companies list
        link = self.browser.find_link_by_href('/companies')
        link.click()
        assert itp('Companies created this week') == True

        # Pages through some results
        flbh = self.browser.find_link_by_href
        flbh('/companies?page=2').click()
        assert itp('Page 2 of 4') == True

    def martin_login(self):
        ''' Convenience function to login the martin user. '''
        url = 'http://localhost:5000/auth/login'
        self.browser.visit(url)
        self.browser.fill('username', 'martin')
        self.browser.fill('password', 'martin')
        self.browser.find_by_name('submit').first.click()

    def test_user_can_post(self):
        self.martin_login()

        # User looks at their profile, notices the 'New Post' button
        url = 'http://localhost:5000/edit_profile'
        self.browser.visit(url)
        itp = self.browser.is_text_present
        assert itp('New Post') == True

        # Clicks it
        # Fills out the form, submits it
        flbh = self.browser.find_link_by_href
        flbh('/my_posts').click()
        assert itp('Say something') == True
        self.browser.fill('post', 'Simulated post from tester')
        self.browser.find_by_name('submit').first.click()

        # Sees their new post on the 'my posts' page
        assert itp('Simulated post from tester') == True

        # Clicks explore, sees their post at the top of the list
        self.browser.visit('http://localhost:5000/explore')
        assert itp('Simulated post from tester') == True
