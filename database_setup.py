# import sqlalchemy

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Hotel(Base):
    __tablename__ = 'hotel'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id
            }


class HotelInfo(Base):
    __tablename__ = 'hotel_info'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(1000))
    price = Column(String(8))
    category = Column(String(250))
    hotel_id = Column(Integer, ForeignKey('hotel.id'))
    hotel = relationship(Hotel)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'category': self.category,
            'user_id': self.user_id,
            'hotel_id': self.hotel_id
        }


engine = create_engine('sqlite:///hotelcatalogwithusers.db')

Base.metadata.create_all(engine)
