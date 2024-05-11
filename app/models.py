from sqlalchemy import String, ForeignKey, Column, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped
from flask_login import UserMixin
from typing import List, Optional
import os

from app import app, db


favourites = db.Table(
    'favourites',
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('cafe_id', ForeignKey('cafe.id'), primary_key=True)
)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[str] = mapped_column(String(250))
    ratings: Mapped[List['Rating']] = relationship(back_populates='user', cascade='all, delete-orphan')
    favourite_cafes: Mapped[List['Cafe']] = relationship(secondary=favourites)
    comments: Mapped[List['Comment']] = relationship(back_populates='user', cascade='all, delete-orphan')

    def is_admin(self):
        return self.email == os.environ.get('ADMIN_EMAIL')


class Cafe(db.Model):
    __tablename__ = 'cafe'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    map_url: Mapped[str] = mapped_column(String(250))
    img_url: Mapped[str] = mapped_column(String(250))
    location: Mapped[str] = mapped_column(String(100))
    has_sockets: Mapped[bool]
    has_toilet: Mapped[bool]
    has_wifi: Mapped[bool]
    can_take_calls: Mapped[bool]
    seats: Mapped[Optional[str]] = mapped_column(String(100))
    coffee_price: Mapped[Optional[str]] = mapped_column(String(100))
    average_rating: Mapped[Optional[float]]
    ratings: Mapped[List['Rating']] = relationship(back_populates='cafe', cascade='all, delete-orphan')
    comments: Mapped[List['Comment']] = relationship(back_populates='cafe', cascade='all, delete-orphan')

    def to_dict(self):
        dictionary = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        dictionary['comments'] = [comment for comment in self.comments]
        return dictionary


class Rating(db.Model):
    __tablename__ = 'rating'
    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range_check'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='ratings')
    cafe_id: Mapped[int] = mapped_column(ForeignKey('cafe.id'))
    cafe: Mapped['Cafe'] = relationship(back_populates='ratings')

    __table_args__ = (
        UniqueConstraint('user_id', 'cafe_id', name='user_unique_cafe_rating'),
    )


class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='comments')
    cafe_id: Mapped[int] = mapped_column(ForeignKey('cafe.id'))
    cafe: Mapped['Cafe'] = relationship(back_populates='comments')


with app.app_context():
    db.create_all()
