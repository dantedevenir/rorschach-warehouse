from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, DateTime
from .base import BaseModel
from db.base import Session

session = Session()

class SnapShot(BaseModel):
    __tablename__ = "snapshot"
    
    entity_id = Column(ForeignKey('snapshots.entity.id'), nullable=False)
    entity = relationship("Entity", back_populates="snapshots", primaryjoin="SnapShot.entity_id == Entity.id")

    provider_id = Column(ForeignKey('providers.provider.id'), nullable=False)
    provider = relationship("Provider", back_populates="snapshots", primaryjoin="SnapShot.provider_id == Provider.id")
    
    timestamp = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    status = Column(ForeignKey('policies.status.id'))
