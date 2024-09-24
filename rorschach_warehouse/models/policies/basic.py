from sqlalchemy import Boolean, Column
from .base import BaseModel
from mapping import mapping_policy_basic

class Basic(BaseModel):
    __tablename__ = 'basic'
    
    for name in mapping_policy_basic.keys():
        locals()[name] = Column(Boolean, default=False, nullable=False)
