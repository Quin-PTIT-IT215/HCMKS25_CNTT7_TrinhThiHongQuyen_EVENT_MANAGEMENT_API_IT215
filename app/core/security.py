import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer

def hash_password(password: str, cost_factor: int = 12):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds= cost_factor)
    hashed_byte = bcrypt.hashpw(password_bytes, salt)
    return hashed_byte.decode('utf-8')

def verify_password(password: str, hashed_password: str):
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_access_token(data: dict):
    to_encode = data.copy()

    # tính time hết hạn
    expire = datetime.now(timezone.utc) + timedelta(minutes= settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    # lý và tạo chuỗi token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm= settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms= [settings.ALGORITHM]
    )

    return payload