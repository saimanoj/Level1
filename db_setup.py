import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(250), nullable=False, unique=True)
    pass_word = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'user_name': self.user_name,
            'pass_word': self.pass_word,
            'id': self.id,
        }


class Item(Base):
    __tablename__ = 'vendor'

    id = Column(Integer, primary_key=True)
    product_id      = Column(String(250), nullable=False)
    product_name    = Column(String(250), nullable=False)
    weave           = Column(String(250))
    composition     = Column(String(250))
    color           = Column(String(250))
    category_1      = Column(String(250))
    category_2      = Column(String(250))
    category_3      = Column(String(250))
    user_id         = Column(Integer, ForeignKey('user.id'), nullable=False)
    user            = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'product_id':self.product_id,
            'product_name': self.product_name,
            'weave':self.weave,
            'composition':self.composition,
            'color':self.color,
            'category_1':self.category_1,
            'category_2':self.category_2,
            'category_3':self.category_3,
            'user_id': self.user_id,
        }


class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True)
    order_id        = Column(String(250), nullable=False)
    product_code    = Column(String(250), nullable=False)
    order_type      = Column(String(250))
    delivery_distance     = Column(String(250))
    delivery_time   = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'order_id':self.order_id,
            'product_code': self.product_code,
            'order_type':self.order_type,
            'delivery_distance':self.delivery_distance,
            'delivery_time':self.delivery_time
        }    


class Product(Base):
    __tablename__ = 'product'

    id                = Column(Integer, primary_key=True)
    product_id        = Column(String(250), nullable=False)
    product_code      = Column(String(250), nullable=False)
    composition       = Column(String(250))
    color             = Column(String(250))
    pattern           = Column(String(250))
    weave             = Column(String(250))
    image_link        = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'product_id':self.product_id,
            'product_code': self.product_code,
            'composition':self.composition,
            'color':self.color,
            'pattern':self.pattern,
            'weave':self.weave,
            'image_link':self.image_link,
        }

engine = create_engine('sqlite:///fm.db')
Base.metadata.create_all(engine)
