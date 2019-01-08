from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Category, Base, Item
 
engine = create_engine('sqlite:///categoryitem.db')
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



#Menu for UrbanBurger
category1 = Category(name = "Mid Cap")

session.add(category1)
session.commit()

itemItem2 = Item(name = "Anaplan", description = "A company provides planning service on the cloud", category = category1)

session.add(itemItem2)
session.commit()


itemItem1 = Item(name = "Adaptive Insights", description = "Planning tool company purchased by Workdays", category = category1)

session.add(itemItem1)
session.commit()




#Menu for Super Stir Fry
category2 = Category(name = "Small Cap")

session.add(category2)
session.commit()


itemItem1 = Item(name = "Rite Aid", description = "Distribute pharmaceutical products", category = category2)

session.add(itemItem1)
session.commit()

itemItem2 = Item(name = "Solar Tech", description = " A start up selling solar pannels", category = category2)

session.add(itemItem2)
session.commit()



print "added companies!"
