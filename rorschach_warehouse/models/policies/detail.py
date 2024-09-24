from sqlalchemy import Boolean, Column
from .base import BaseModel
from mapping import mapping_policy_detail

class Detail(BaseModel):
    __tablename__ = 'detail'
    
    for name in mapping_policy_detail.keys():
        locals()[name] = Column(Boolean, default=False, nullable=False)
