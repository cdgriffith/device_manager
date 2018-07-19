# FlaskBootstrap
Generic starting point for a standard flask project

Designed for:

* Python 3.6+ 
* Linux

Run the setup to rename everything to your own project name.

```bash
python -m venv venv
source venv/bin/activate
pip install reusables

python project_setup.py
```

Create your own config file at device_manager.config.yaml 

Should contain the following items:

```yaml
env: production
host: 0.0.0.0
port: 8080 # Should match the one in device_manager.nginx
session_secret: bad_secret  # make real one with os.urandom(32).hex()
```


Run the project:

```bash
pip install -r requirements.txt
python -m device_manager
```

## Deploy for device_manager

As on Ubuntu 18.04

As root:
```
apt update
apt install nginx python3-venv python3-pip apache2-utils -y
mkdir /var/log/device_manager
addgroup device_manager
adduser device_manager device_manager
htpasswd -c /etc/nginx/.htpasswd <admin_user>

# make the three directories of the current live site (src), backup duirng deploy (backup) and staged files for deployment (staging)

mkdir -p /opt/device_manager /opt/device_manager/src /opt/device_manager/staging /opt/device_manager/backup

# Copy project to /opt/device_manager/src/

chown -R device_manager:device_manager /opt/device_manager
sudo -u device_manager bash -c "python3 -m venv /opt/device_manager/venv"
sudo -u device_manager bash -c "/opt/device_manager/venv/bin/pip install -r /opt/device_manager/src/requirements.txt --no-cache"

# copy SSL certificate to /etc/ssl/certs/device_manager.crt
# copy SSL key to /etc/ssl/private/device_manager.key

cp /opt/device_manager/src/device_manager.nginx /etc/nginx/sites-available/device_manager
chown root:root /etc/nginx/sites-available/device_manager
chmod 0644 /etc/nginx/sites-available/device_manager
ln -s /etc/nginx/sites-available/device_manager /etc/nginx/sites-enabled/device_manager
rm /etc/nginx/sites-enabled/default

cp /opt/device_manager/src/device_manager.service /etc/systemd/system/device_manager.service
chown root:root /etc/systemd/system/device_manager.service
chmod 0755 /etc/systemd/system/device_manager.service
systemctl daemon-reload
systemctl enable  /etc/systemd/system/device_manager.service
systemctl start device_manager.service

# Modify /etc/nginx/nginx.conf, add under http
# client_max_body_size 2M;

service nginx restart

```
