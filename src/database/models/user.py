__all__ = ["User"]

from sqlalchemy import Column, BigInteger, String, Float, Integer

from src.database.__mixin__ import IdMixin
from src.database.models.base import Base


class User(Base, IdMixin):
    __tablename__ = 'user'

    tg_id = Column(BigInteger, unique=True, index=True, nullable=False)
    user_name = Column(String(255), nullable=False)
    gender = Column(String(10))
    age = Column(Integer)
    height = Column(Float)
    weight = Column(Float)
    activity = Column(Float)
    goal = Column(String(50))
