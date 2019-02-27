''' Starting point for the flask application. 
run with:
export FLASK_APP=frameapp.py
pipenv run flask run
'''
from app import create_app, db
from app.models import User, Post, Crawled, Subscriber

# This is where the application gets initialized
app = create_app()


''' Shell context enables easier debugging by running:
pipenv run flask shell

Then you will be dropped into the python REPL loop, and you can do
things like:
User.query.all()
'''
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Crawled': Crawled,
            'Subscriber': Subscriber}
