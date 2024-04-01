from sqlalchemy import Integer, String, ForeignKey, Text
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


with app.app_context():
    db.create_all()
