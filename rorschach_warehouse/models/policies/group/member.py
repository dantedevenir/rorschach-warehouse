from sqlalchemy import Boolean, Column, ForeignKey
from ..base import BaseModel
from mapping import mapping_member

class Member(BaseModel):
    __tablename__ = 'member'
    
    group_id = Column(ForeignKey("policies.group.id"), nullable=False)

    type_id = Column(ForeignKey("policies.member_type.id"), nullable=False)

    for name in mapping_member.keys():
        locals()[name] = Column(Boolean, default=False, nullable=False)
