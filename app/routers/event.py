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


@router.get('events', response_model= APIResponse)
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

    staff = (
        db.query(EventStaff)
        .filter(
            EventStaff.event_id == event_id,
            EventStaff.user_id == current_user.id
        )
        .first()
    )

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
    
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Sự kiện không tồn tại"
        )

    if event.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Chỉ owner mới được thêm thành viên"
        )

    user = db.query(User).filter(
        User.id == member_data.user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Người dùng không tồn tại"
        )


    existing_member = db.query(EventStaff).filter(
        EventStaff.event_id == event_id,
        EventStaff.user_id == member_data.user_id
    ).first()

    if existing_member is not None:
        raise HTTPException(
            status_code=409,
            detail="Người dùng đã là thành viên của sự kiện"
        )

    new_member = EventStaff(
        event_id=event_id,
        user_id=member_data.user_id,
        role="Member",
        joined_at= datetime.now(timezone.utc)
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return APIResponse(
    statusCode= status.HTTP_201_CREATED,
    data= new_member,
    message= "Thêm thành viên thành công",
    timestamp= datetime.now(timezone.utc),
    path= f"/events/{event_id}/members",
    error= None
)