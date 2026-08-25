from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin
from app.schemas.response import APIResponse
from app.models.user import User
from app.core.security import hash_password, verify_password
from app.core.exceptions import bad_request
from datetime import datetime, timezone
from fastapi import HTTPException, status

def create_user(user_data: UserCreate, db: Session, response_model= APIResponse):  
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise bad_request('Email đã tồn tại')

    hashed_pwd = hash_password(user_data.password)

    new_user = User(
        email = user_data.email,
        password_hash = hashed_pwd,
        full_name = user_data.full_name,
        created_at=datetime.now(timezone.utc)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return APIResponse(
        statusCode=201,
        data={
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at
        },
        message="Đăng ký thành công",
        timestamp=datetime.now(timezone.utc),
        path="/api/auth/register",
        error=None
    )


def user_login(db: Session, user_data: UserLogin):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= 'Email hoặc mật khẩu không đúng'
        )

    if not user.is_active:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail= 'Tài khoản bị khóa'
        )
    
    return user

