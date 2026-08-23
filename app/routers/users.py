from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse
from app.db.database import get_db
from app.core.security import create_access_token
from app.models.user import User
from app.dependencies.user import get_current_user, require_admin

router = APIRouter(
    prefix= '/api/user',
    tags= ['Authentication']
)

@router.get('/me', response_model= UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get('/admin')
def admin_test(
    current_user: User = Depends(require_admin)
):
    return {
        "message": "Bạn là Admin"
    }

@router.get(
    "",
    response_model=list[UserResponse]
)
def get_users(
    name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(User)

    if name:
        query = query.filter(
            User.full_name.ilike(f"%{name}%")
        )

    if email:
        query = query.filter(
            User.email.ilike(f"%{email}%")
        )

    if is_active is not None:
        query = query.filter(
            User.is_active == is_active
        )

    return query.all()