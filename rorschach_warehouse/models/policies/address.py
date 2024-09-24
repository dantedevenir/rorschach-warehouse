from sqlalchemy import Boolean, Column
from .base import BaseModel
from mapping import mapping_address

class Address(BaseModel):
    __tablename__ = 'address'
    
    for name in mapping_address.keys():
        locals()[name] = Column(Boolean, default=False, nullable=False)
