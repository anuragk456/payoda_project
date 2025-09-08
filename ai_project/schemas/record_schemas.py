from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

class OptionType(str, Enum):
    opportunity = "opportunity"
    search = "search"

class StatusType(str, Enum):
    active = "active"
    inactive = "inactive"

class RecordCreate(BaseModel):
    option_type: OptionType
    description: Optional[str] = None
    status: Optional[StatusType] = StatusType.active

class RecordUpdate(BaseModel):
    option_type: Optional[OptionType] = None
    description: Optional[str] = None
    status: Optional[StatusType] = None

class RecordOut(BaseModel):
    id: int
    created_at: datetime
    option_type: OptionType
    description: Optional[str]
    status: StatusType

    class Config:
        from_attributes = True
