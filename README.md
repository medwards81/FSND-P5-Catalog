# Linux Server Configuration - Project Overview
This project involved deploying a web application on virtual server.
More specifically, a Flask Python application running on Ubuntu.
Below are some of steps and resources I used to accomplish this.

### Server Info
- The IP address of the server is: 52.41.217.228
- The URL path to the web application is: http://ec2-52-41-217-228.us-west-2.compute.amazonaws.com

### Steps, Resources Used and Software Installed
1) ***Create a new user and grant user sudo permission***

-- Resource: https://www.digitalocean.com/community/tutorials/how-to-add-and-delete-users-on-an-ubuntu-14-04-vps

2) ***Update and upgrade all currently installed packages***

-- Resource: http://askubuntu.com/questions/94102/what-is-the-difference-between-apt-get-update-and-upgrade

3) ***Configure the local timezone to UTC***

-- Resource: http://askubuntu.com/questions/138423/how-do-i-change-my-timezone-to-utc-gmt

4) ***Change SSH port to 2200***

-- Resource: https://help.ubuntu.com/community/SSH/OpenSSH/Configuring

5) ***Configure the Uncomplicated Fire Wall (UFW)***

-- Resource: https://help.ubuntu.com/community/UFW

6) ***Install and configure Apache to serve a Python mod_wsgi application***

-- Software installed (using apt-get): apache2, python-setuptools, libapache2-mod-wsgi, python-dev, python-pip, virtualenv

-- Resource: http://blog.udacity.com/2015/03/step-by-step-guide-install-lamp-linux-apache-mysql-python-ubuntu.html

-- Resource: https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps

7) ***Install Git and clone the Catalog App***

-- Software installed (using apt-get): git

8) ***Install and Configure PostgresSQL***

-- Software installed (using apt-get): postgresql, postgresql-contrib

-- Resource: https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps