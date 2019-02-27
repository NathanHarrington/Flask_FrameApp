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

## Deploying on EC2
<pre>

# Launch a Fedora 29 Cloud Base Images for [Amazon Public
# Cloud](https://alt.fedoraproject.org/cloud/).

# Use the 'Standard HVM AMIs' for lower cost, not SSD
# Click the 'click to launch' button, then choose the datacenter by
# clicking the cloud next to launch.

# Choose the instance:
# General purpose, t2.micro, Free tier eligible, 1CPU, 1Gb RAM, EBS only

# Using google domains, Assign A record for your domain to point to this
# server.  Google domains is the best option as it has 'privacy' on by
# default which costs extra most other places.

# Accept all defaults, connect to the instance with:
ssh \
    -i your_key_pair.pem \
    -R 6622:localhost:22 \
    fedora@amazon-ec2-public-dnsname

dnf update -y
timedatectl set-timezone America/New_York
reboot

# If you don't reboot after changing the timezone, it appears to 
# lockup randomly

# On the EC2 instance, change the amazon security group to have ports open:
# 22, 80, 6787, 443

# Edit the ssh server configuration: 
# Change ssh port to a different port number
#   Port <port number>
# Enable remote port tunneling
#   GatewayPorts yes
vi /etc/ssh/sshd_config

dnf -y install git policycoreutils-python-utils supervisor nginx

# Save the file above, then open the port:
semanage port -a -t ssh_port_t -p tcp <port number>

# Reboot, verify your configuration on <port number>
    
# change 'enforcing' to 'permissive'
vi /etc/selinux/config
reboot


# Clone from your local ssh to enforce having to type in your password
# every time and not needing to have the github credentials on the
# production system
mkdir /home/fedora/projects
cd /home/fedora/projects/
git clone ssh://username@localhost:6622/home/username/projects/Flask_FrameApp

cd ~/projects/Flask_FrameApp
# With system python, make sure pipenv is installed. Not --user land
# python, pipenv in system python
pip install pipenv

# Now that pipenv is installed, setup this environmentt 
pipenv install --dev
pipenv shell

python setup.py develop
export FLASK_APP=frameapp.py
# On windows use:
#  set FLASK_APP=frameapp.py

# Clear db migrations, re-init database
rm -rf migrations
flask db init
flask db migrate
flask db upgrade


# Now that application data is prepared, setup the WSGI interface
pipenv install gunicorn

# Create secret key, put inside .env file, then manually edit to remove
# newline
echo 'SECRET_KEY=' > .env
python3 -c "import uuid; print(uuid.uuid4().hex)" >> .env


# start gunicorn, make sure it works independently:
pipenv run gunicorn -b localhost:8000 -w 4 frameapp:app
(ctrl-c)


# Copy the supervisord configuration file to supervisor location
cp deployment/supervisor/frameapp_supervisor.ini \
    /etc/supervisord.d/


# Restart supervisord daemon
systemctl enable supervisord
systemctl restart supervisord
supervisorctl reload

# Create self-signed certificates for this testing application only


# Configure nginx
cp /etc/nginx/nginx.conf /etc/nginx/backup.nginx.conf
cp deployment/nginx/system_wide_nginx.conf /etc/nginx/nginx.conf
cp deployment/nginx/frameapp_nginx.conf /etc/nginx/conf.d/

systemctl enable nginx
systemctl restart nginx

# Connect to the EC2 domain name with a browser, confirm security
# exception for the self-signed certificate
</pre>

## Optional: Request a new certificate using Lets Encrypt
<pre>
# One-time certificate creation using Lets Encrypt
# Simplest way to do this appears to be to make a simple nginx
# configuration that is the default that ships with fedora plus:
vi /etc/nginx/nginx.conf

location ~ /.well-known {
    root /usr/share/nginx/;
}

# Verify with a dry run:
export DOMAIN=yourdomain.com
sudo certbot certonly --webroot -w /usr/share/nginx/ -d $DOMAIN --dry-run

# Run the actual
sudo certbot certonly --webroot -w /usr/share/nginx/ -d $DOMAIN

# Copy the real files, to a separate repository for backup
cp -r  /etc/letsencrypt/archive/$DOMAIN/ \
    /home/fedora/projects/LE_${DOMAIN}/archive_${DOMAIN}.com


# After complete, reset to the nginx configuration for the flask
frameapp located in deployment/nginx
cp deployment/nginx/system_wide_nginx.conf /etc/nginx/nginx.conf
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


