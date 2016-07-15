from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Movie, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response, flash, abort
import requests
from functools import wraps


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Movie Catalog"

# Connect to database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# check login status wrapper function
# Based on: http://flask.pocoo.org/docs/0.10/patterns/viewdecorators/       
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("Please login to access this feature.")
            return redirect(url_for('showLogin', next=request.url))
    return decorated_function

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
    #return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# Home - show all genres
@app.route('/')
@app.route('/genre/')
def showGenres():
    genres = session.query(Genre).order_by(asc(Genre.name))
    if 'username' not in login_session:
        return render_template('publicGenres.html', genres=genres)
    else:
        return render_template('genres.html', genres=genres)


# Create a new genre
@app.route('/genre/new/', methods=['GET', 'POST'])
@login_required
def newGenre():
    if request.method == 'POST':
        newGenre = Genre(
            name=request.form['name'], description=request.form['description'],
            user_id=login_session['user_id'])
        session.add(newGenre)
        session.commit()
        flash('New genre added.')
        return redirect(url_for('showGenres'))
    else:
        return render_template('newGenre.html')


# Edit a genre
@app.route('/genre/<int:genre_id>/edit/', methods=['GET', 'POST'])
@login_required
def editGenre(genre_id):
    editedGenre = session.query(
        Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedGenre.name = request.form['name']
            editedGenre.description = request.form['description']
            flash('Genre successfully updated.')
            return redirect(url_for('showGenreMovies', genre_id=genre_id))
    else:
        return render_template(
            'editGenre.html', genre=editedGenre)


# Delete a genre
@app.route('/genre/<int:genre_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteGenre(genre_id):
    genreToDelete = session.query(
        Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        session.delete(genreToDelete)
        session.commit()
        flash('Genre successfully deleted.')
        return redirect(
            url_for('showGenres', genre_id=genre_id))
    else:
        return render_template(
            'deleteGenre.html', genre=genreToDelete)


# Show a llist of movies by genre
@app.route('/genre/<int:genre_id>/')
@app.route('/genre/<int:genre_id>/movies/')
def showGenreMovies(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    movies = session.query(Movie).filter_by(
        genre_id=genre_id).order_by(asc(Movie.name)).all()
    creator = getUserInfo(genre.user_id)
    if 'username' not in login_session:
        return render_template('publicGenreMovies.html', genre=genre,
                    movies=movies)
    else:
        return render_template('genreMovies.html', genre=genre, movies=movies,
            creator=creator, user_id=login_session['user_id'])


# Show a specific movie
@app.route('/genre/<int:genre_id>/movie/<int:movie_id>/')
@app.route('/genre/<int:genre_id>/movies/movie/<int:movie_id>/')
def showMovie(genre_id, movie_id):
    movie = session.query(Movie).filter_by(id=movie_id).one()
    genre = session.query(Genre).filter_by(id=genre_id).one()
    creator = getUserInfo(movie.user_id)
    if 'username' not in login_session:
        return render_template('publicMovie.html', movie=movie)
    else:
        return render_template('movie.html', movie=movie, creator=creator,
                    user_id=login_session['user_id'])


# Create a new movie
@app.route(
    '/genre/<int:genre_id>/addMovie/', methods=['GET', 'POST'])
@login_required
def newMovie(genre_id):
    if request.method == 'POST':
        newMovie = Movie(
            name=request.form['name'], genre_id=genre_id,
            plot=request.form['plot'], user_id=login_session['user_id'],
            year=request.form['year'], picture=request.form['picture'])
        session.add(newMovie)
        session.commit()
        flash('New movie added.')
        return redirect(url_for('showGenreMovies', genre_id=genre_id))
    else:
        genre = session.query(Genre).filter_by(id=genre_id).one()
        return render_template('newMovie.html', genre=genre, genre_id=genre_id)


# Edit a movie
@app.route('/genre/<int:genre_id>/movie/<int:movie_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editMovie(genre_id, movie_id):
    editedMovie = session.query(Movie).filter_by(id=movie_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedMovie.name = request.form['name']
        if request.form['genre']:
            editedMovie.genre_id = request.form['genre']
        if request.form['year']:
            editedMovie.year = request.form['year']
        if request.form['plot']:
            editedMovie.plot = request.form['plot']
        if request.form['picture']:
            editedMovie.picture = request.form['picture']
        session.add(editedMovie)
        session.commit()
        flash('Movie successfully updated.')
        return redirect(url_for('showGenreMovies',
                                genre_id=genre_id))
    else:
        genres = session.query(Genre).all()
        return render_template(
            'editMovie.html', genre_id=genre_id, movie_id=movie_id,
            movie=editedMovie, genres=genres)


# Delete a movie
@app.route('/genre/<int:genre_id>/movie/<int:movie_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteMovie(genre_id, movie_id):
    movieToDelete = session.query(Movie).filter_by(id=movie_id).one()
    if request.method == 'POST':
        session.delete(movieToDelete)
        session.commit()
        flash('Movie successfully deleted.')
        return redirect(url_for('showGenreMovies', genre_id=genre_id))
    else:
        return render_template('deleteMovie.html', movie=movieToDelete)


# JSON endpoints
@app.route('/catalog/JSON')
@app.route('/catalog/json')
def moviesJSON():
    movies = session.query(Movie).all()
    return jsonify(movies=[m.serialize for m in movies])


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    #stored_credentials = login_session.get('credentials')
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    #login_session['credentials'] = credentials
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = '&nbsp;'
    #output += '<h1>Welcome, '
    #output += login_session['username']
    #output += '!</h1>'
    #output += '<img src="'
    #output += login_session['picture']
    #output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    #output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s." % login_session['username'])
    print "done!"
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    #credentials = login_session.get('credentials')
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    #access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

''' Will add Fb connect at a later time

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=' \
            'fb_exchange_token&client_id=' \
            '%s&client_secret=%s&fb_exchange_token=%s' % (
            app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0' \
          '&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = '&nbsp;'
    #output += '<h1>Welcome, '
    #output += login_session['username']

    #output += '!</h1>'
    #output += '<img src="'
    #output += login_session['picture']
    #output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    #output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("You are now logged in as %s." % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?' \
          'access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out"
'''

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            #del login_session['credentials']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have been successfully logged out.")
        return redirect(url_for('showGenres'))
    else:
        flash("You were not logged in.")
        return redirect(url_for('showGenres'))


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None
        
        
# Protect against cross site request forgery
# This will create a session token which will need to be added to forms
# that make post requests
# Code taken from: http://flask.pocoo.org/snippets/3/        
@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = login_session.pop('_csrf_token', None)
        if not token or (token != request.form.get('_csrf_token') 
            and token != request.args.get('_csrf_token')):
            abort(403)

def generate_csrf_token():
    if '_csrf_token' not in login_session:
        token = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for x in range(32))
        login_session['_csrf_token'] = token
    return login_session['_csrf_token']
    

app.jinja_env.globals['csrf_token'] = generate_csrf_token 


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
