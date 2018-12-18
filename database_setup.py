import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):

    __tablename__ ='category'

    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

class Item(Base):

    __tablename__= 'item'
    
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

# We added this serialize function to be able to send JSON objects in a
# serializable format
    @property
    def serialize(self):

        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'category_id':self.category_id,
            'category_name':self.category.name
        }


#### put this at end of file
engine= create_engine('sqlite:///categoryitem.db')
Base.metadata.create_all(engine)
