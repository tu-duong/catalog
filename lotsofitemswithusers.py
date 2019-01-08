from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Category, Base, Item, User
 
engine = create_engine('sqlite:///categoryitemwithusers.db')
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
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


#Menu for UrbanBurger

category3 = Category(name = "Large Cap")

session.add(category3)
session.commit()


category1 = Category(name = "Mid Cap")

session.add(category1)
session.commit()

itemItem2 = Item(user_id=1, name = "Anaplan", description = "A company provides planning service on the cloud", category = category1)

session.add(itemItem2)
session.commit()


itemItem1 = Item(user_id=1, name = "Adaptive Insights", description = "Planning tool company purchased by Workdays", category = category1)

session.add(itemItem1)
session.commit()




#Menu for Super Stir Fry
category2 = Category(name = "Small Cap")

session.add(category2)
session.commit()


itemItem1 = Item(user_id=1,name = "Rite Aid", description = "Distribute pharmaceutical products", category = category2)

session.add(itemItem1)
session.commit()

itemItem2 = Item(user_id=1, name = "Solar Tech", description = " A start up selling solar pannels", category = category2)

session.add(itemItem2)
session.commit()


category4 = Category(name = "Micro Cap")

session.add(category4)
session.commit()

print "added companies!"
