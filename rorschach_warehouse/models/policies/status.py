from sqlalchemy import Column, Enum
from .enum import Status
from .base import BaseModel


class StatusMaster(BaseModel):
    __tablename__ = "status"
    
    name = Column(Enum(Status), unique=True)