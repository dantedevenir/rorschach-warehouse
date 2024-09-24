from ..base import BaseModel
from sqlalchemy import Column, ForeignKey, String


class Source(BaseModel):
    __tablename__ = "source"
    
    name = Column(String, unique=True)
    type = Column(ForeignKey('providers.source_type.id'))