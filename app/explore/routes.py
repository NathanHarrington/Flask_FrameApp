''' Handle routes specific to the explore functionality. Shows reuse of
    models and flask_login outside the auth blueprint.
'''
from flask import render_template
from flask_login import login_required
from app.models import Post, Crawled
from app.explore import bp


@bp.route('/explore')
@login_required
def explore():
    # What a long query can look like
    posts = Post.query.order_by(Post.timestamp.desc()).limit(3)
    posts_total = Post.query.count()

    # Split into multiple lines, which makes it easier to read
    cqo = Crawled.query.order_by
    ccd = Crawled.crawl_date.desc
    companies = cqo(ccd()).limit(3)
    companies_total = Crawled.query.count()

    rt = render_template
    return rt('explore/explore_index.html', title='Explore',
              posts=posts, companies=companies,
              posts_total=posts_total, companies_total=companies_total)
