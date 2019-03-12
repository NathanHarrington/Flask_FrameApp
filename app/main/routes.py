''' Handle routes for main application functionality. '''
from datetime import datetime, timedelta
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from math import ceil

from app import db
from app.main.forms import EditProfileForm
from app.main.forms import CrawledForm, SubscriberForm
from app.models import User, Post, Crawled, Subscriber
from app.main import bp

# Example of an application-wide pre-request function. Tests where the
# user is authenticated before any other functionlity.
@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

def build_stats():
    ''' Compute the number of companies added to the crawler database
        within the past week and month, return as a dictionary.
    '''
    stats = {}

    qry = db.session.query

    one_week_ago = datetime.utcnow() - timedelta(weeks=1)
    date_filter = (Crawled.crawl_date > one_week_ago)
    weekly = qry(Crawled).filter(date_filter).count()

    one_month_ago = datetime.utcnow() - timedelta(weeks=4.3)
    date_filter = (Crawled.crawl_date > one_month_ago)
    monthly = qry(Crawled).filter(date_filter).count()

    stats = {'weekly_count': weekly,
             'monthly_count': monthly}
    return stats


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    ''' Show the home page summary, and a form to sign up for an email
    update. 
    '''
    form = SubscriberForm()
    if form.validate_on_submit():
        subscriber = Subscriber(email=form.email.data)
        db.session.add(subscriber)
        db.session.commit()
        flash('You have been subscribed to updates!')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['POSTS_PER_PAGE']

    companies = Crawled.query.paginate(page, per_page, False)
    page_max = ceil(companies.total / per_page)
    companies.page_max = page_max

    next_url = None
    if companies.has_next:
        next_url = url_for('main.index', page=companies.next_num)

    prev_url = None
    if companies.has_prev:
        prev_url = url_for('main.index', page=companies.prev_num)

    stats = build_stats()

    rt = render_template
    result = rt('companies_index.html', title='Home',
                form=form, companies=companies, stats=stats,
                next_url=next_url, prev_url=prev_url)

    return result

@bp.route('/user/<username>')
@login_required
def user(username):
    ''' View details on a specific user. '''
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    ''' Show the users current profile, and a form to change their
        profile information. 
    '''
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    ''' With the currently logged in user, add a user to follow. '''
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %(username)s not found.', username=username)
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following %(username)s!', username=username)
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    ''' With the currently logged in user, stop following a user. '''
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %(username)s not found.', username=username)
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %(username)s.', username=username)
    return redirect(url_for('main.user', username=username))

@bp.route('/companies')
@login_required
def companies():
    ''' Show a summary of the current companies. '''
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['POSTS_PER_PAGE']

    companies = Crawled.query.paginate(page, per_page, False)
    page_max = ceil(companies.total / per_page)
    companies.page_max = page_max

    next_url = None
    if companies.has_next:
        next_url = url_for('main.companies', page=companies.next_num)

    prev_url = None
    if companies.has_prev:
        prev_url = url_for('main.companies', page=companies.prev_num)

    stats = build_stats()

    rt = render_template
    result = rt('companies_index.html', title='Home',
                companies=companies, stats=stats,
                next_url=next_url, prev_url=prev_url)
    return result


@bp.route('/new_company', methods=['GET', 'POST'])
def new_company():
    ''' Provide a simple interface to add a new company. Use html and
    expect the user to populate the form by hand. '''
    form = CrawledForm()
    if form.validate_on_submit():
        cr = Crawled
        company = cr(ein_number=form.ein_number.data,
                 company_type=form.company_type.data,
                 certificate_type=form.certificate_type.data,
                 company_name=form.company_name.data,
                 street_address=form.street_address.data,
                 city=form.city.data,
                 state=form.state.data,
                 zip_code=form.zip_code.data,
                 phone=form.phone.data,
                 crawl_date=form.crawl_date.data
                )
        db.session.add(company)
        db.session.commit()
        flash('Added a company: %s' % form.ein_number.data)
        return redirect(url_for('main.new_company'))

    return render_template('new_company.html', title='New company', form=form)


@bp.route('/json_new_company', methods=['PUT'])
def json_new_company():
    ''' Only permit a json submission of new company data. Does not
    require login. Bare bones example of a JSON API.
    '''
    data = request.get_json() or {}
    # loader sends a string of format:
    # 2019-02-11 10:04:07.196493
    date_frmt = '%Y-%m-%d %H:%M:%S.%f'
    new_date = datetime.strptime(data['crawl_date'], date_frmt)
    data['crawl_date'] = new_date

    company = Crawled()
    company.from_dict(data)

    db.session.add(company)
    db.session.commit()

    response = jsonify(company.to_dict())
    return response

@bp.route('/fail')
def fail_on_purpose():
    ''' Trigger a 500 error in order to verify the flask error template
    rewriting tests.
    '''
    db.session.add(Borked)
