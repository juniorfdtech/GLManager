from sqlalchemy import Column, DateTime, func

from app.data.config import Base
from app.serializers import Serializer


class BaseEntity(Base, Serializer):
    __abstract__ = True

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __init__(self, **kwargs):
        Serializer.__init__(self, **kwargs)
