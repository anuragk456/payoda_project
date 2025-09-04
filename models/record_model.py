from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Text,
    Enum as SAEnum,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OptionType(str, Enum):
    OPPORTUNITY = "opportunity"
    SEARCH = "search"

class StatusType(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    option_type = Column(SAEnum(OptionType), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SAEnum(StatusType), nullable=False, default=StatusType.ACTIVE)
