from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Genre, Movie, User

## Note: some of the comments below are verbatim from lesson 3 of the Full Stack Foundations course by Udacity
## They were too good not to leave in

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="Ewe Dasity", email="ewe.dacity@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


# Populate our comedies
desc_comedy = "A genre of film that uses humor as a driving force. The aim of a comedy film is " \
              "to illicit laughter from the audience through entertaining stories and characters."
Genre1 = Genre(user_id=1, name="Comedy", description=desc_comedy)
session.add(Genre1)
session.commit()

plot = "Twenty years since their first adventure, Lloyd and Harry go on a road trip to find Harry's newly " \
       "discovered daughter, who was given up for adoption."

Comedy1 = Movie(user_id=1, name="Dumb and Dumber", genre=Genre1, plot=plot)

session.add(Comedy1)
session.commit()

plot = "A group of juvenile criminals is sent for vacation to Kamp Kikakee. The clumsy Ernest has to " \
       " care for them, although he doesn't even know how to take care of himself."

Comedy2 = Movie(user_id=1, name="Earnest Goes to Camp", genre=Genre1, plot=plot)

session.add(Comedy2)
session.commit()

plot = "A group of good-hearted but incompetent misfits enter the police academy, but the instructors " \
       "there are not going to put up with their pranks."

Comedy3 = Movie(user_id=1, name="Police Academy", genre=Genre1, plot=plot)

session.add(Comedy3)
session.commit()

# Populate our dramas
desc_drama = "A genre of narrative fiction (or semi-fiction) intended to " \
             "be more serious than humorous in tone, focusing on in-depth development " \
             "of realistic characters who must deal with realistic emotional struggles."
Genre2 = Genre(user_id=1, name="Drama", description=desc_drama)

session.add(Genre2)
session.commit()

plot = "A lawyer sees the chance to salvage his career and self-respect by taking a medical malpractice case " \
       " to trial rather than settling."

Drama1 = Movie(user_id=1, name="The Verdict", genre=Genre2, plot=plot)

session.add(Drama1)
session.commit()

plot = "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son."

Drama2 = Movie(user_id=1, name="The Godfather", genre=Genre2, plot=plot)

session.add(Drama2)
session.commit()

plot = "An in-depth examination of the ways in which the U.S. Vietnam war impacts and disrupts the lives " \
       "of people in a small industrial town in Pennsylvania."

Drama3 = Movie(user_id=1, name="The Deer Hunter", genre=Genre2, plot=plot)

session.add(Drama3)
session.commit()


print "Added movies to catalog!"
