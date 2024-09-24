from sqlalchemy import Boolean, Column
from .base import BaseModel
from mapping import mapping_policy_auth

class Auth(BaseModel):
    __tablename__ = 'auth'
    
    for name in mapping_policy_auth.keys():
        locals()[name] = Column(Boolean, default=False, nullable=False)
