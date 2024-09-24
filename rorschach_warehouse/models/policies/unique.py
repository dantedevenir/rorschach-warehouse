from sqlalchemy import Boolean, Column
from .base import BaseModel
from mapping import mapping_primary_id, mapping_secondary_id

class Unique(BaseModel):
    __tablename__ = 'unique'
    
    for name in mapping_primary_id.keys():
        locals()[name] = Column(Boolean, default=False, nullable=False)
    
    for name in mapping_secondary_id.keys():
        locals()[name] = Column(Boolean, default=False, nullable=False)
