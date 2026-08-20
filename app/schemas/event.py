from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime

class EventBase(BaseModel):
    name: str = Field(..., min_length= 1, max_length= 255)
    description: str | None = Field(default= None, max_length= 255)

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: str | None = Field(default= None, min_length= 1, max_length= 255)
    description: str | None = Field(default= None, max_length= 255)

class EventResponse(EventBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes= True)

