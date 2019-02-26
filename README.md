Flask_FrameApp is designed to be the baseline project for the next level
of Cordince customer facing experiments. The main design goals are:

![Travis Build Stats](https://travis-ci.com/NathanHarrington/Flask_FrameApp.svg?branch=master)
![Appveyor Build Stats](https://ci.appveyor.com/api/projects/status/mojjlxt7dg5s2s6a/branch/master?svg=true)
<pre>
Flask-style minimal application development 

Truly test driven development. Write the users behavior in a functional
test, make the individual unit tests required for any new features,
repeat until the test passes.

Develop on Windows and Linux with pipenv

MVC Architecture:
Well defined interfaces for easier testability

100% Test Coverage:
Use pytest and geckodriver with splinter to click buttons and simulate
an operator.

Continuous Integration ready:
Example travis configuration
Example appveyor configuration

Deployment instructions:
EC2 -> Nginx -> and all the associated free tier goodness

This is based heavily on the [Flask
Mega-tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
</pre>

## Installation
<pre>
# With system python, make sure pipenv is installed:
pip install pipenv

# Now that pipenv is installed, setup this environmentt 
pipenv install --dev
pipenv shell

python setup.py develop
export FLASK_APP=frameapp.py
# On windows use:
#  set FLASK_APP=frameapp.py

flask db init
flask db migrate
flask db upgrade
export FLASK_DEBUG=1
flask run
</pre>

## Run tests:
<pre>
# Make sure firefox is installed on the system, separate from the geckodriver
pipenv shell
export PATH=$PWD/scripts/:$PATH
# On windows use:
#  set FLASK_APP=frameapp.py
py.test --verbose tests/
</pre>

## Utilities, examples
<pre>
# Load the example database in other pipenv shell
python scripts/load_example_posts.py 10 10
python scripts/load_example_companies.py 100 'http://localhost:5000'

## Testing email configuration
pipenv shell
python -m smtpd -n -c DebuggingServerocalhost:8025

# In a separate window:
export MAIL_SERVER=localhost
export MAIL_PORT=8025
# On MS-Windows run:
#  set MAIL_SERVER=localhost
#  set MAIL_PORT=8025

flask run
#  Create user with bob@example.com
#  Login -> Reset Password -> bob@example.com
#  Look in the first terminal windows, click the link printed to log,
#     verify that the password can be changed
</pre>



## Instructions for installation on Windows alongside miniconda
<pre>
Download the most recent Python (3.7.2) from here:
https://www.python.org/downloads/windows

Make sure to choose the 64 bit version

Run the installer, accept all defaults. Do not run the option to expand the path length.

Edit your environment variables
Find the lines that says:
c:\Users\nharrington\Miniconda3
c:\Users\nharrington\Miniconda3\Scripts
Above those lines add:
C:\Users\nharrington\AppData\Local\Programs\Python\Python37
C:\Users\nharrington\AppData\Local\Programs\Python\Python37\Scripts

Start a new windows command prompt, run:
python --version
Verify that the version of python is what you downloaded and 'conda' does not appear anywhere in the python version
</pre>


