## Generate your own self-signed certificate

<pre>
# These files generated with command:
openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
  -keyout certs/key.pem -out certs/cert.pem
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

