from sqlalchemy import Integer, String, ForeignKey, Text, Boolean, Float, Column
from sqlalchemy.orm import relationship, mapped_column, Mapped
from flask_login import UserMixin
from typing import List, Optional

from app import app, db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    occupation = Mapped[Optional[str]]
    ratings: Mapped[List['Rating']] = relationship(back_populates='user', cascade='all, delete-orphan')


class Cafe(db.Model):
    __tablename__ = 'cafe'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    map_url: Mapped[str] = mapped_column(String(250))
    image_url: Mapped[str] = mapped_column(String(250))
    location: Mapped[str] = mapped_column(String(100))
    has_sockets: Mapped[bool] = mapped_column(Boolean)
    has_toilet: Mapped[bool] = mapped_column(Boolean)
    has_wifi: Mapped[bool] = mapped_column(Boolean)
    can_take_calls: Mapped[bool] = mapped_column(Boolean)
    seats: Mapped[str] = mapped_column(String(100))
    coffee_price: Mapped[str] = mapped_column(String(100))
    average_rating: Mapped[Optional[float]]
    ratings: Mapped[List['Rating']] = relationship(back_populates='cafe', cascade='all, delete-orphan')


class Rating(db.Model):
    __tablename__ = 'rating'
    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='ratings')
    cafe_id: Mapped[int] = mapped_column(ForeignKey('cafe.id'))
    cafe: Mapped['Cafe'] = relationship(back_populates='ratings')


favorites = db.Table(
    'favourites',
    Column('user_id', ForeignKey(User.id), primary_key=True),
    Column('cafe_id', ForeignKey(Cafe.id), primary_key=True)
)

with app.app_context():
    db.create_all()
