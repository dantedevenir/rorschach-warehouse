from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped
from .base import BaseModel

class Statement(BaseModel):
    __tablename__ = 'statement'
    
    entity_id: Mapped[int] = Column(ForeignKey("snapshots.entity.id", ondelete="CASCADE"))
    unique_id: Mapped[int] = Column(ForeignKey("policies.unique.id", ondelete="CASCADE"))
    basic_id: Mapped[int] = Column(ForeignKey("policies.basic.id", ondelete="CASCADE"))
    auth_id: Mapped[int] = Column(ForeignKey("policies.auth.id", ondelete="CASCADE"))
    detail_id: Mapped[int] = Column(ForeignKey("policies.detail.id", ondelete="CASCADE"))
    address_id: Mapped[int] = Column(ForeignKey("policies.address.id", ondelete="CASCADE"))
    group_id: Mapped[int] = Column(ForeignKey("policies.group.id", ondelete="CASCADE"))