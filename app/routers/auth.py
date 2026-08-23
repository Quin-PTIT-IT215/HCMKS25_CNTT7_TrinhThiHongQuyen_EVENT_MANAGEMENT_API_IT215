from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin
from app.schemas.response import APIResponse
from app.services.user import create_user, user_login
from app.db.database import get_db
from datetime import datetime, timezone
from app.core.security import create_access_token, create_refresh_token, decode_refresh_token
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

router = APIRouter(
    prefix= '/api/auth',
    tags= ['Authentication']
)

class RefreshTokenRequets(BaseModel):
    refresh_token: str 


@router.post('/register', response_model= APIResponse)
def register(
    email: str = Form(..., description= 'Email của người dùng'),
    password : str = Form(..., description= 'Mật khẩu'),
    full_name : str = Form(..., description= 'Tên người dùng'),
    db: Session = Depends(get_db)):

    user_data = UserCreate(email = email, full_name= full_name, password= password)
    new_user = create_user(user_data= user_data, db= db)

    return new_user

@router.post('/login', response_model= APIResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_data = UserLogin(email= form_data.username, password= form_data.password)
    user = user_login(db, user_data)
    role_name = user.role if user.role else None
    access_token = create_access_token(data= {'sub': user.email, 'id': user.id, 'role': role_name})
    refresh_token = create_refresh_token(data= {'sub': user.email, 'id': user.id, 'role': user.role})

    return APIResponse(
        statusCode= 200,
        data= {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at
            }
        },
        message= 'Đăng nhập thành công',
        timestamp= datetime.now(timezone.utc),
        path= '/api/auth/login',
        error= None
    )

@router.post('/refresh')
def refresh_access_token(data: RefreshTokenRequets):
    try:
        payload = decode_refresh_token(data.refresh_token)

    except ValueError as e:
        raise HTTPException(
            status_code= 401,
            detail= str(e)
        )

    new_access_token = create_access_token({
        'sub': payload['sub'],
        'id': payload['id']
    })

    return {
        'access_token': new_access_token,
        'token_type': 'bearer'
    }