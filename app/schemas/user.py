from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.schemas.response import APIResponse


class UserBase(BaseModel):
    email: EmailStr = Field(..., min_length= 5, max_length= 255)
    full_name: str = Field(..., min_length= 1, max_length= 255)

class UserCreate(UserBase):
    password: str = Field(..., min_length= 6)
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError('Họ tên không được để trống')
            
        return value

    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        value = value.strip()

        if not value:
            raise ValueError( 'Mật khẩu không được chỉ chứa khoảng trắng')
        
        return value

class UserUpdate(BaseModel):
    full_name: str | None = Field(default= None, min_length= 1, max_length= 255)
    is_active: bool | None = None

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at : datetime

    model_config = ConfigDict(from_attributes= True)

class UserLogin(BaseModel):
    email: EmailStr = Field(..., min_length= 5, max_length= 255)
    password: str = Field(..., min_length= 6)



