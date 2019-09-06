[![Travis Build Stats](https://travis-ci.org/NathanHarrington/Flask_FrameApp.svg?branch=master)](https://travis-ci.org/NathanHarrington/Flask_FrameApp) [![Appveyor Build Stats](https://ci.appveyor.com/api/projects/status/mojjlxt7dg5s2s6a/branch/master?svg=true)](https://ci.appveyor.com/project/NathanHarrington/flask-frameapp/) [![Coverage Status](https://coveralls.io/repos/github/NathanHarrington/Flask_FrameApp/badge.svg)](https://coveralls.io/github/NathanHarrington/Flask_FrameApp) [![Maintainability](https://api.codeclimate.com/v1/badges/3b701b307fd95be1142a/maintainability)](https://codeclimate.com/github/NathanHarrington/Flask_FrameApp/maintainability) [![codecov](https://codecov.io/gh/NathanHarrington/Flask_FrameApp/branch/master/graph/badge.svg)](https://codecov.io/gh/NathanHarrington/Flask_FrameApp)



### The baseline project for the next level of Cordince customer facing experiments. The main design goals are:

<pre>
Flask-style minimal application development 

Bootstrap 4

Fully contained content delivery for network-limited contexts.

Truly test driven development. Write the users behavior in a functional
test, make the individual unit tests required for any new features,
repeat until the test passes.

Develop on Windows and Linux with pipenv

MVC Architecture:
Well defined interfaces for easier testability

100% Test Coverage:
Use pytest to click buttons and simulate an operator.

Continuous Integration ready:
Example travis configuration
Example appveyor configuration
Coverage and Maintainability badges

Deployment instructions:
Amazon Web Services EC2 -> Nginx -> and all the associated free tier goodness
Lets Encrypt SSL certificates

This is based heavily on the [Flask Mega-tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
</pre>
![Example Layout](/docs/flask_frameapp_demo.png "Flask_FrameApp demo")


## Installation
<pre>
# With system python, make sure pipenv is installed:
pip install pipenv

# Now that pipenv is installed, setup this environmentt 
pipenv install --dev

pipenv run python setup.py develop
export FLASK_APP=frameapp.py
# On windows use:
#  set FLASK_APP=frameapp.py

export FLASK_DEBUG=1
pipenv run flask db init
pipenv run flask db migrate
pipenv run flask db upgrade
pipenv run flask run
</pre>

## Run tests:
<pre>
py.test --verbose tests/test_units.py
py.test --verbose tests/test_functional.py

# Check coverage statistics:
pipenv run py.test --disable-pytest-warnings tests/test_units.py \
    --cov=app --cov-report term-missing


## Testing email configuration
pipenv run python -m smtpd -n -c DebuggingServer localhost:8025

# In a separate window:
export MAIL_SERVER=localhost
export MAIL_PORT=8025
# On MS-Windows run:
#  set MAIL_SERVER=localhost
#  set MAIL_PORT=8025

pipenv run flask run
#  Create user with bob@example.com
#  Login -> Reset Password -> bob@example.com
#  Look in the first terminal windows, click the link printed to log,
#     verify that the password can be changed
## Utilities, examples
</pre>

## Loading data 
<pre>
# These examples show you how to get data into the system in a variety
# of ways
# First, start the application in a separate window:
pipenv run flask run

# Then load the database through direct access and API:
pipenv run python scripts/load_example_posts.py 10 10
pipenv run python scripts/load_example_companies.py 100 'http://localhost:5000'
</pre>

## Deploying on EC2
<pre>
# Launch a Fedora 29 Cloud Base Images for [Amazon Public Cloud](https://alt.fedoraproject.org/cloud/).

# Use the 'Standard HVM AMIs' for lower cost, not SSD
# Click the 'click to launch' button, then choose the datacenter by
# clicking the cloud next to launch.

# Choose the instance:
# General purpose, t2.micro, Free tier eligible, 1CPU, 1Gb RAM, EBS only

# Using google domains, configure your domain to support web requests on
# www.domain only. Any request to domain.com will be automatically
# redirected to www.domain.com
# The google domains DNS Configuration is:
#
# Synthetic records:
#        subdomain forward of:
#                @ -> www.newclia.com
#                Temporary redirect (302)
#                Do not forward path
#                Disable SSL
#
# Custom Resource Records:
#        www     A       <AWS EC2 ip address>



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
    
# change 'enforcing' to 'permissive'
vi /etc/selinux/config
reboot

# Verify connection on ssh port 6787 instead of 22
ssh \
    -o port=6787 \
    -i your_key_pair.pem \
    -R 6622:localhost:22 \
    fedora@amazon-ec2-public-dnsname

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

pipenv run python setup.py develop
export FLASK_APP=frameapp.py
# On windows use:
#  set FLASK_APP=frameapp.py

# Clear db migrations, re-init database
rm -rf migrations
pipenv run flask db init
pipenv run flask db migrate
pipenv run flask db upgrade


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

# Configure nginx
cp /etc/nginx/nginx.conf /etc/nginx/backup.nginx.conf
cp deployment/nginx/system_wide_nginx.conf /etc/nginx/nginx.conf
cp deployment/nginx/frameapp_nginx.conf /etc/nginx/conf.d/

systemctl enable nginx
systemctl restart nginx

# If you see 403 permission denied errors when attempting to serve
# static files, you can try:
#  sudo chmod 710 /home/fedora
#  sudo usermod -a -G fedora nginx
#  chown -R nginx.nginx app/static
#  sudo systemctl restart nginx
#  (Reboot may be required)

# Connect to the EC2 domain name with a browser, confirm security
# exception for the self-signed certificate
</pre>

## Lets Encrypt Certificate Generation
<pre>
# Use certbot to create a lets encrypt certificate for the website. Make
# sure to follow the instructions above for redirecting all bare domain
# requests to www.domain.com first.

# Make a backup of your existing config
cp /etc/nginx/nginx.conf /etc/nginx/pre.letsencrypt.nginx.conf
cp /etc/nginx/original.system.nginx.conf /etc/nginx/nginx.conf

dnf install certbot

# Create a simple nginx  configuration based on the default that ships with
# fedora. In /etc/nginx/nginx.conf Find the lines that say:

	location / {
	}

# Directly underneath, add:

	location ~ /.well-known {
		root /usr/share/nginx/;
	}

# Restart nginx with default config, and a known configuration for
# certbot
systemctl restart nginx

# Verify with a dry run, where YOURDOMAIN is the full www.yourdomain.com
sudo certbot certonly --webroot -w /usr/share/nginx/ -d YOURDOMAIN --dry-run

# Run the actual
sudo certbot certonly --webroot -w /usr/share/nginx/ -d YOURDOMAIN

# Immediately make a copy of the certbot generated files to a backup location:
cp -r /etc/letsencrypt/archive/YOURDOMAIN \
	~/projects/my_lets_encrypt_backup_YOURDOMAIN.$(date +%Y%m%d)

# Overwrite this projects self-signed certs with the lets encrypt versions:
cp /etc/letsencrypt/archive/YOURDOMAIN/fullchain1.pem \
    ~/projects/Flask_FrameApp/certs/fullchain1.pem

cp /etc/letsencrypt/archive/YOURDOMAIN/cert1.pem \
    ~/projects/Flask_FrameApp/keys/cert1.pem

cp /etc/letsencrypt/archive/YOURDOMAIN/privkey1.pem \
    ~/projects/Flask_FrameApp/keys/privkey1.pem

# Reset to the original configuration, which now uses the lets encrypt
# certifications instead of the self-signed certificates
cp /etc/nginx/pre.letsencrypt.nginx.conf /etc/nginx/nginx.conf
systemctl restart nginx

</pre>

## Lets Encrypt Certificate Renewal
<pre>
# Create a backup of the live configuration
sudo cp /etc/nginx/nginx.conf /etc/nginx/pre-renew.letsencrypt.nginx.conf

# Find the lines that say location / like above, and directly underneath, add:
	location ~ /.well-known {
		root /usr/share/nginx/;
	}

# YOURDOMAIN is a full www.domain.com type domain
export YOURDOMAIN=www.domain.com
export PROJECT=~/projects/Flask_FrameApp
export SRC=/etc/letsencrypt/live/$YOURDOMAIN/

sudo certbot certonly --webroot -w /usr/share/nginx/ -d $YOURDOMAIN --dry-run

# Run without dry run
# If it says it's not close to expiry, select renew
sudo certbot certonly --webroot -w /usr/share/nginx/ -d $YOURDOMAIN

# Immediately make a copy of the certbot generated files to a backup location:
sudo cp -r /etc/letsencrypt/archive/$YOURDOMAIN \
        ~/projects/my_lets_encrypt_backup_${YOURDOMAIN}.$(date +%Y%m%d)


# Overwrite this projects self-signed certs with the lets encrypt versions:

sudo cp $SRC/fullchain.pem $PROJECT/certs/fullchain1.pem
sudo cp $SRC/cert.pem $PROJECT/certs/cert1.pem
sudo cp $SRC/privkey.pem $PROJECT/certs/privkey1.pem
sudo cp $SRC/chain.pem $PROJECT/certs/chain1.pem

sudo systemctl restart nginx

# The approach here is to leave the certificate files in the folder,
# unversioned. This prevents you from committing them to a source
# repository by mistake. It does let a raw directory level backup pickup
# the cert files automatically.

</pre>

## Instructions for installation on Windows alongside miniconda
<pre>
Download the most recent Python (3.7.2) from here:
https://www.python.org/downloads/windows

Make sure to choose the 64 bit version

Run the installer, accept all defaults. Do not run the option to expand the path length.

Edit your environment variables
Find the lines that says:
c:\Users\username\Miniconda3
c:\Users\username\Miniconda3\Scripts
Above those lines add:
C:\Users\username\AppData\Local\Programs\Python\Python37
C:\Users\username\AppData\Local\Programs\Python\Python37\Scripts

Start a new windows command prompt, run:
python --version
Verify that the version of python is what you downloaded and 'conda' does not appear anywhere in the python version
</pre>


## Favicon generation
<pre>
The configuration presented here was built by:
1. Build a 1024x1024 svg icon.
2. Upload it to realfavicongenerator.net
3. Extract the provided package into static/favicons, tweak as necessary

</pre>
