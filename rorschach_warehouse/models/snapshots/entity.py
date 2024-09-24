from sqlalchemy import BigInteger, Column, Integer, String
from sqlalchemy.orm import relationship
from .base import BaseModel
from mapping import mapping_primary_id, mapping_secondary_id

mapping_ids = mapping_primary_id.copy()
mapping_ids.update(mapping_secondary_id)

class Entity(BaseModel):
    __tablename__ = 'entity'
    
    for name, value in mapping_ids.items():
        if value == str:
            locals()[name] = Column(String, default=False, nullable=False)
        if value == int:
            locals()[name] = Column(Integer, default=False, nullable=False)
        if value == [int]:
            locals()[name] = Column(BigInteger, default=False, nullable=False)
    
    snapshots = relationship("SnapShot")
    statements = relationship("Statement")