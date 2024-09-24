from .enum import SourceType
from ..base import BaseModel
from sqlalchemy import Column, Enum


class SourceTypeMaster(BaseModel):
    __tablename__ = "source_type"

    name = Column(Enum(SourceType), unique=True)