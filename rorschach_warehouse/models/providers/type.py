from .enum import Type
from .base import BaseModel
from sqlalchemy import Column, Enum
    
class TypeMaster(BaseModel):
    __tablename__ = "type"
    
    name = Column(Enum(Type), unique=True)