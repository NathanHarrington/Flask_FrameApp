''' Connect to the database
Use the model
Create new objects
Commit with sqlalchemy
See load example companies for what a load can look like via HTTP
'''

import sys, json
from random import randint, shuffle

from app import db
from app.models import User, Post

from app import create_app
app = create_app()

if len(sys.argv) != 3:
    print('Specify total to users, total posts')
    sys.exit(1)

total_users = int(sys.argv[1])
total_posts = int(sys.argv[2])

firsts  = ['Bob', 'Dave', 'Fred', 'Marshall']
lasts   = ['Harris', 'Johns', 'Jones', 'Smith']
domains = ['gmail.com', 'example.com', 'hotmail.com', 'bluehost.com']
post_words = ['In', 'the', 'story', 'there', 'was', 'stuff']

for item in range(total_users):
    shuffle(firsts)
    shuffle(lasts)
    shuffle(domains)

    username = '%s %s%s' % (firsts[0], lasts[0], item)

    email = '%s@%s%s' % (firsts[0], domains[0], item)
    print('Add: %s' % email)

    new_user = User(username=username, email=email)
    with app.app_context():
        db.session.add(new_user)

        for post_item in range(total_posts):
            shuffle(post_words)
            body = ' '.join(post_words)
            body += ' Post number: %s' % post_item

            # Walk through each user, add N posts
            post = Post(body=body, author=new_user)
            db.session.add(post)

        db.session.commit()
