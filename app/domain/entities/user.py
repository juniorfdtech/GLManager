from sqlalchemy import String, DateTime, Column, Integer
from .base import BaseEntity


class User(BaseEntity):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    connection_limit = Column(Integer, nullable=False)
    expiration_date = Column(DateTime, nullable=False)

    def __str__(self) -> str:
        return f'{self.id} - {self.username}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.id}, {self.username})'
