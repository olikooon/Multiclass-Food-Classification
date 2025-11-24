__all__ = ["Meal"]

from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, func

from src.database.__mixin__ import IdMixin
from src.database.models.base import Base


class Meal(Base, IdMixin):
    __tablename__ = 'meals'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String)
    grams = Column(Float)
    kcal = Column(Float)
