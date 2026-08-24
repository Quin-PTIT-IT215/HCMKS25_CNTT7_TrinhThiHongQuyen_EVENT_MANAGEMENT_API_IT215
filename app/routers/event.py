from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.db.database import get_db
from app.schemas.response import APIResponse
from app.schemas.event_staff import EventStaffCreate
from app.models.user import User
from app.models.event import Event, EventStaff
from app.models.event_task import EventTask
from datetime import datetime, timezone
from app.dependencies.user import get_current_user

router = APIRouter(
    prefix= '/events',
    tags= ['Events']
)

@router.post('/event', response_model= APIResponse, status_code= status.HTTP_201_CREATED)
def create_evevt(
    event_data: EventCreate,
    curren_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = Event(
        name = event_data.name,
        description = event_data.description,
        owner_id = curren_user.id,
        created_at = datetime.now(timezone.utc)
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    event_staff = EventStaff(
        event_id = event.id,
        user_id = curren_user.id,
        role = 'Owner',
        joined_at = datetime.now(timezone.utc)
    )

    db.add(event_staff)
    db.commit()

    return APIResponse(
        statusCode = status.HTTP_201_CREATED,
        data = EventResponse.model_validate(event),
        message = "Tạo sự kiện thành công",
        timestamp = datetime.now(timezone.utc),
        path = "/api/events",
        error = None
    )


@router.get('', response_model= APIResponse)
def get_events(
    name: str | None = Query(default= None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = (
        db.query(Event).outerjoin(EventStaff, Event.id == EventStaff.event_id).filter((Event.owner_id == current_user.id) | (EventStaff.user_id == current_user.id))
    )

    if name:
        query = query.filter(Event.name.ilike(f"%{name.strip()}%"))

    events = (query.distinct().order_by(Event.created_at.desc()).all())

    data = [
        EventResponse.model_validate(event)
        for event in events
    ]

    response = APIResponse(
        statusCode=200,
        data=data,
        message="Lấy danh sách sự kiện thành công",
        timestamp=datetime.now(timezone.utc),
        path="/api/events",
        error=None
    )

    return response


@router.get('/{event_id}', response_model= APIResponse)
def get_event(event_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code= 404,
            detail= 'Sự kiện không tồn tại'
        )

    is_owner = event.owner_id == current_user.id
    is_menber = db.query(EventStaff).filter(EventStaff.event_id == event_id, EventStaff.user_id == current_user.id).first()

    if not is_owner and not is_menber:
        raise HTTPException(
            status_code= 403,
            detail= 'Bạn không phải thành viên của sự kiện'
        )

    return APIResponse(
        statusCode= 200,
        data= EventResponse.model_validate(event),
        message= "Lấy chi tiết sự kiện thành công",
        timestamp= datetime.now(timezone.utc),
        path= f"/api/events/{event_id}",
        error= None
    )


@router.patch('/{event_id}', response_model= APIResponse)
def update_event(
    event_id : int,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code= 404,
            detail= 'Sự kiện không tồn tại'
        )

    if event.owner_id != current_user.id:
        raise HTTPException(
            status_code= 403,
            detail= 'Chỉ OWNER mới được sửa sự kiện'
        )

    update_data = event_data.model_dump(exclude_unset= True)
    if 'name' in update_data:
        update_data['name'] = update_data['name'].strip()

        if not update_data['name']:
            raise HTTPException(
                status_code= 422,
                detail= 'Tên sự kiện không được để trống'
            )

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return APIResponse(
        statusCode= 200,
        data= EventResponse.model_validate(event),
        message= 'Cập nhật sự kiện thành công',
        timestamp= datetime.now(timezone.utc),
        path= f'/api/events/{event_id}',
        error= None
    )



@router.delete('/{event_id}', response_model=APIResponse)
def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail='Sự kiện không tồn tại'
        )


    if event.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail='Chỉ OWNER mới được xóa sự kiện'
        )

    # Xóa các EventTask của Event
    db.query(EventTask).filter(
        EventTask.event_id == event_id
    ).delete(
        synchronize_session=False
    )

    # Xóa các thành viên của Event
    db.query(EventStaff).filter(
        EventStaff.event_id == event_id
    ).delete(
        synchronize_session=False
    )

    # Xóa Event
    db.delete(event)

    db.commit()

    return APIResponse(
        statusCode= 200,
        data= None,
        message= 'Xóa sự kiện thành công',
        timestamp= datetime.now(timezone.utc),
        path= f'/api/events/{event_id}',
        error= None
    )


@router.post(
    '/{event_id}/members',
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED
)
def add_event_member(
    event_id: int,
    member_data: EventStaffCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Kiểm tra event tồn tại
    event = (db.query(Event).filter(Event.id == event_id).first())

    if event is None:
        raise HTTPException(
            status_code=404,
            detail='Sự kiện không tồn tại'
        )

    # Chỉ owner mới được thêm member
    if event.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail='Chỉ OWNER mới được thêm thành viên'
        )

    # Kiểm tra user tồn tại
    user = (db.query(User).filter(User.id == member_data.user_id).first())

    if user is None:
        raise HTTPException(
            status_code=404,
            detail='Người dùng không tồn tại'
        )

    # Không cho owner tự thêm chính mình
    if user.id == event.owner_id:
        raise HTTPException(
            status_code=409,
            detail='OWNER đã là thành viên của sự kiện'
        )

    # Kiểm tra user đã là member chưa
    existing_member = (
        db.query(EventStaff)
        .filter(
            EventStaff.event_id == event_id,
            EventStaff.user_id == member_data.user_id
        )
        .first()
    )

    if existing_member is not None:
        raise HTTPException(
            status_code=409,
            detail='Người dùng đã là thành viên của sự kiện'
        )

    
    new_member = EventStaff(
        event_id=event_id,
        user_id=member_data.user_id,
        role='Member',
        joined_at=datetime.now(timezone.utc)
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return APIResponse(
        statusCode=status.HTTP_201_CREATED,
        data={
            'event_id': new_member.event_id,
            'user_id': new_member.user_id,
            'role': new_member.role,
            'joined_at': new_member.joined_at
        },
        message='Thêm thành viên thành công',
        timestamp=datetime.now(timezone.utc),
        path=f'/api/events/{event_id}/members',
        error=None
    )


@router.delete(
    '/{event_id}/members/{user_id}',
    response_model=APIResponse
)
def remove_event_member(
    event_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Kiểm tra event tồn tại
    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail='Sự kiện không tồn tại'
        )

    # Chỉ owner mới được xóa member
    if event.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail='Chỉ OWNER mới được xóa thành viên'
        )

    # Không được xóa chính owner
    if user_id == event.owner_id:
        raise HTTPException(
            status_code=400,
            detail='Không được xóa OWNER của sự kiện'
        )

    # Tìm member
    member = (
        db.query(EventStaff)
        .filter(
            EventStaff.event_id == event_id,
            EventStaff.user_id == user_id
        )
        .first()
    )

    if member is None:
        raise HTTPException(
            status_code=404,
            detail='Người dùng không phải thành viên của sự kiện'
        )

    # Không được xóa Owner dựa trên role
    if member.role == 'Owner':
        raise HTTPException(
            status_code=400,
            detail='Không được xóa OWNER của sự kiện'
        )

    db.delete(member)
    db.commit()

    return APIResponse(
        statusCode=200,
        data=None,
        message='Xóa thành viên thành công',
        timestamp=datetime.now(timezone.utc),
        path=f'/api/events/{event_id}/members/{user_id}',
        error=None
    )


@router.get(
    '/{event_id}/members',
    response_model=APIResponse
)
def get_event_members(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Kiểm tra event tồn tại
    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail='Sự kiện không tồn tại'
        )

    # Kiểm tra người dùng có quyền xem danh sách member
    is_owner = event.owner_id == current_user.id

    is_member = (
        db.query(EventStaff)
        .filter(
            EventStaff.event_id == event_id,
            EventStaff.user_id == current_user.id
        )
        .first()
    )

    if not is_owner and is_member is None:
        raise HTTPException(
            status_code=403,
            detail='Bạn không phải thành viên của sự kiện'
        )

    # Lấy danh sách member
    members = (
        db.query(EventStaff)
        .filter(EventStaff.event_id == event_id)
        .all()
    )

    data = []

    for member in members:
        user = (
            db.query(User)
            .filter(User.id == member.user_id)
            .first()
        )

        data.append({
            'event_id': member.event_id,
            'user_id': member.user_id,
            'email': user.email,
            'full_name': user.full_name,
            'role': member.role,
            'joined_at': member.joined_at
        })

    return APIResponse(
        statusCode=200,
        data=data,
        message='Lấy danh sách thành viên thành công',
        timestamp=datetime.now(timezone.utc),
        path=f'/api/events/{event_id}/members',
        error=None
    )