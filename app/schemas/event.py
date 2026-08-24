from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime

class EventBase(BaseModel):
    name: str = Field(..., min_length= 1, max_length= 255)
    description: str | None = Field(default= None, max_length= 255)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Tên sự kiện không được để trống")

        return value

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: str | None = Field(default= None, min_length= 1, max_length= 255)
    description: str | None = Field(default= None, max_length= 255)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None):
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Tên sự kiện không được để trống")

        return value
    

class EventResponse(EventBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes= True)

