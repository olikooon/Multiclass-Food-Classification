__all__ = ["Calories"]

from sqlalchemy import Column, String, Float

from src.database.__mixin__ import IdMixin
from src.database.models.base import Base


class Calories(Base, IdMixin):
    __tablename__ = 'calories'

    name = Column(String, unique=True, index=True)
    kcal_per_100 = Column(Float)
