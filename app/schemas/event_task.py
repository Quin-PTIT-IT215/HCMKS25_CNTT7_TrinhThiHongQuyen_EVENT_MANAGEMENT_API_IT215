from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class EventTaskStatus(str, Enum):
    TODO = "Todo"
    IN_PROGRESS = "In_progress"
    DONE = "Done"

class EventTaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class EventTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    due_date: datetime | None = None
    priority: EventTaskPriority = EventTaskPriority.MEDIUM

class EventTaskCreate(EventTaskBase):
    assignee_id: int | None = None

class EventTaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    assignee_id: int | None = None
    status: EventTaskStatus | None = None
    priority: EventTaskPriority | None = None
    due_date: datetime | None = None


class EventTaskResponse(EventTaskBase):
    id: int
    event_id: int
    assignee_id: int | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)