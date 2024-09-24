from sqlalchemy import Column, ForeignKey, Enum, MetaData
from sqlalchemy.orm import relationship
from ..base import BaseModel

class Group(BaseModel):
    __tablename__ = 'group'
   
    members = relationship("Member")
