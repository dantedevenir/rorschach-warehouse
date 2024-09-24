from .base import BaseModel
from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.orm import relationship

class Provider(BaseModel):
    __tablename__ = "provider"
    
    name = Column(ForeignKey("providers.name.id"))
    type = Column(ForeignKey("providers.type.id"))
    source = Column(ForeignKey("providers.source.id"))
    
    snapshots = relationship("SnapShot")