# Move Catalog App

## Section 0: Intro
This application allows you to create a catlog of movies stored by genre.  Logged in users can create their own genres and add, edit and delte movies.
Content created by other users may only be viewed.

## Section 1: Set Up Environment
Install Git, Vagrant and VirtualBox if not already installed 

## Section 2: Requirements
Flask
sqlalchemy
database_setup
random
string
oauth2client.client
httplib2
json
requests
functools

## Section 3: Installation
Set up the vagrant environment by cloning the following github repository: https://github.com/udacity/fullstack-nanodegree-vm.git

## Section 4: Set Up
-Open up your favorite command shell
-Inside the vagrant directory, run the command: vagrant up
-This will intialize the server running in VirtualBox
-Then run the command: vagrant ssh
-This will grant access to the server
-Navigate to /vagrant/catalog

## Section 5: How to run
-Set up the sqllite database by running the command: python database_setup.py
-Now populate the database via the command: python populate_database.py
-Now start up the movie catalog application by running the command: python application.py 

## Section 6: Usage
-On the home screen, you will see the genres listed.
-Click on a genre to see the movies that are part of that genre.  You can then view the movies individually.
-In order to create your own genres and movies, you'll need to login via the login button at the top right of the screen.
-Please note thaty ou'll need a Google account to login.
-Have fun!