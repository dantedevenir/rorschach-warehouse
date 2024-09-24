from sqlalchemy import Column, Integer
from db.base import Base

class BaseModel(Base):
    __abstract__ = True
    __allow_unmapped__ = True
    __table_args__ = {'schema': 'policies'}
    
    id = Column(Integer, primary_key=True)