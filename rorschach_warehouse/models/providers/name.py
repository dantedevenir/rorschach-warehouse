from .enum import Name
from .base import BaseModel
from sqlalchemy import Column, Enum
    
class NameMaster(BaseModel):
    __tablename__ = "name"
    
    name = Column(Enum(Name), unique=True)