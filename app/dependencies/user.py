from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.security import decode_access_token
import jwt


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)
# security = HTTPBearer()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    # credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Token không hợp lệ hoặc đã hết hạn",
    #     headers={"WWW-Authenticate": "Bearer"}
    # )

    # token = credentials.credentials

    try:
        payload = decode_access_token(token)

        user_id = payload.get("id")

        if user_id is None:
            raise HTTPException(
                status_code= 401,
                detail= 'Token không hợp lệ'
            )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # except jwt.InvalidTokenError:
    #     raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    # if user is None:
    #     raise credentials_exception

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa"
        )

    return user


def require_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền Admin"
        )

    return current_user