from .enum import MemberType
from ..base import BaseModel
from sqlalchemy import Column, Enum


class MemberTypeMaster(BaseModel):
    __tablename__ = "member_type"

    name = Column(Enum(MemberType), unique=True)