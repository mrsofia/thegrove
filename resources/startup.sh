#!/usr/bin/env bash

# WORK IN PROGRESS

# does all necessary work to set up Flask application upon startup of a fresh server.
# based off the following link:
# https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04

# TODO: add support for more pkg mgrs
sudo apt-get install python3-pip python3-dev nginx

sudo pip3 install virtualenv

mkdir ~/myproject
cd ~/myproject

virtualenv env

source env/bin/activate

pip install uwsgi flask

# TODO: .service file will need to be populate w/ appropriate data before moving. Try a python script.
#   Data to infill includes: User, WorkingDir, Environment, ExecStart
mv /resources/buildserver.service /etc/systemd/system/buildserver.service

systemctl start buildserver
systemctl enable buildserver

# TODO: sites-available file will need to be populated w/ appropriate data as well. Python script might be good.
#   Data to infill includes: server_domain_or_IP, socket file,
mv /resources/buildserver_sites-available /etc/nginx/sites-available/buildserver

ln -s /etc/nginx/sites-available/buildserver /etc/nginx/sites-enabled

systemctl restart nginx

ufw allow 'Nginx Full'
