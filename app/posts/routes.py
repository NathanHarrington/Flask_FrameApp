''' Handle routes specific to the posts functionality. '''
from flask import render_template, current_app, url_for
from flask import redirect, flash
from flask_login import login_required, current_user
from math import ceil
from app import db
from app.models import Post
from app.posts import bp
from app.main.forms import PostForm


@bp.route('/summary')
@login_required
def summary():
    ''' Pagination of posts, showing how to add a class member to the
        posts object and iterate over the items within the template.

        paginate documentation says the page variable is pulled from the
        request automatically if unspecified.
    '''
    per_page = current_app.config['POSTS_PER_PAGE']

    posts = Post.query.paginate(per_page=per_page, error_out=False)
    posts.page_max = ceil(posts.total / per_page)

    next_url = None
    if posts.has_next:
        next_url = url_for('posts.summary', page=posts.next_num)

    prev_url = None
    if posts.has_prev:
        prev_url = url_for('posts.summary', page=posts.prev_num)

    rt = render_template
    return rt('posts/posts_summary.html', title='Posts', posts=posts,
              next_url=next_url, prev_url=prev_url)


@bp.route('/my_posts', methods=['GET', 'POST'])
@login_required
def my_posts():
    ''' Provide a form for adding a new post, show the users most recent
        posts.

        paginate documentation says the page variable is pulled from the
        request automatically if unspecified.
    '''
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('New post created!')
        return redirect(url_for('posts.my_posts'))

    per_page = current_app.config['POSTS_PER_PAGE']

    pqf = Post.query.filter_by

    id_filter = pqf(user_id=current_user.id).order_by(Post.timestamp.desc())

    posts = id_filter.paginate(per_page=per_page, error_out=False)
    posts.page_max = ceil(posts.total / per_page)

    next_url = None
    if posts.has_next:
        next_url = url_for('posts.my_posts', page=posts.next_num)

    prev_url = None
    if posts.has_prev:
        prev_url = url_for('posts.my_posts', page=posts.prev_num)

    return render_template('posts/my_posts.html', form=form,
                           posts=posts,
                           next_url=next_url, prev_url=prev_url)
