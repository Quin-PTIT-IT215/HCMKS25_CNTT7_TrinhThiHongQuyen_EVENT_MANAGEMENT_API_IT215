from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.user import get_current_user
from app.models.user import User
from app.models.event import Event, EventStaff
from app.models.event_task import EventTask
from app.schemas.event_task import (
    EventTaskCreate,
    EventTaskResponse,
    EventTaskUpdate,
    EventTaskStatus,
    EventTaskPriority
)
from app.schemas.response import APIResponse

router = APIRouter(
    prefix="/events",
    tags=["Event Tasks"]
)

@router.post("/{event_id}/event-tasks",
    response_model=EventTaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_event_task(
    event_id: int,
    task_data: EventTaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Kiểm tra event có tồn tại không
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự kiện"
        )

    # Kiểm tra user hiện tại có phải thành viên của event không
    member = db.query(EventStaff).filter(
        EventStaff.event_id == event_id,
        EventStaff.user_id == current_user.id
    ).first()

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của sự kiện"
        )

    # Kiểm tra priority hợp lệ
    if task_data.priority not in ["Low", "Medium", "High"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Priority phải là Low, Medium hoặc High"
        )

    # Nếu có assignee_id thì kiểm tra người được giao
    #    có phải thành viên của event hay không
    if task_data.assignee_id is not None:
        assignee = db.query(EventStaff).filter(
            EventStaff.event_id == event_id,
            EventStaff.user_id == task_data.assignee_id
        ).first()

        if assignee is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người được giao công việc không phải thành viên của sự kiện"
            )

    new_task = EventTask(
        event_id=event_id,
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        priority=task_data.priority.value,
        assignee_id=task_data.assignee_id,
        status="Todo"
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task



@router.get(
    "/{event_id}/event-tasks",
    response_model=list[EventTaskResponse]
)
def get_event_tasks(
    event_id: int,
    status: EventTaskStatus | None = Query(default=None),
    priority: EventTaskPriority | None = Query(default=None),
    assignee_id: int | None = Query(default=None),
    title: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Kiểm tra event có tồn tại không
    event = db.query(Event).filter(
        Event.id == event_id
    ).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự kiện"
        )

    # Kiểm tra user hiện tại có phải thành viên của event không
    member = db.query(EventStaff).filter(
        EventStaff.event_id == event_id,
        EventStaff.user_id == current_user.id
    ).first()

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của sự kiện"
        )

    # Chỉ lấy công việc thuộc event hiện tại
    query = db.query(EventTask).filter(
        EventTask.event_id == event_id
    )

    # Filter theo status
    if status is not None:
        query = query.filter(
            EventTask.status == status.value
        )

    # Filter theo priority
    if priority is not None:
        query = query.filter(
            EventTask.priority == priority.value
        )

    # Filter theo người được giao
    if assignee_id is not None:
        query = query.filter(
            EventTask.assignee_id == assignee_id
        )

    # Search theo title
    if title is not None:
        query = query.filter(
            EventTask.title.ilike(f"%{title}%")
        )

    if sort_by == "created_at":
        sort_column = EventTask.created_at

    elif sort_by == "due_date":
        sort_column = EventTask.due_date

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_by chỉ được là created_at hoặc due_date"
        )

    if sort_order == "asc":
        query = query.order_by(sort_column.asc())

    elif sort_order == "desc":
        query = query.order_by(sort_column.desc())

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_order chỉ được là asc hoặc desc"
        )

    tasks = query.offset(offset).limit(limit).all()

    return tasks


@router.get("/event-tasks/{task_id}",
    response_model=EventTaskResponse
)
def get_event_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(EventTask).filter(EventTask.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy công việc sự kiện"
        )

    member = db.query(EventStaff).filter(
        EventStaff.event_id == task.event_id,
        EventStaff.user_id == current_user.id
    ).first()

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của sự kiện"
        )

    return task


@router.patch(
    "/event-tasks/{task_id}",
    response_model=EventTaskResponse
)
def update_event_task(
    task_id: int,
    task_data: EventTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(EventTask).filter(EventTask.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy công việc sự kiện"
        )

    # Kiểm tra user có thuộc event không
    member = db.query(EventStaff).filter(
        EventStaff.event_id == task.event_id,
        EventStaff.user_id == current_user.id
    ).first()

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của sự kiện"
        )

    # Chỉ Owner hoặc Assignee mới được cập nhật
    if (member.role != "Owner" and task.assignee_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền cập nhật công việc này"
        )

    # Chỉ lấy những trường client thực sự gửi lên
    update_data = task_data.model_dump(
        exclude_unset=True
    )

    if "status" in update_data:
        if update_data["status"] not in [
            "Todo",
            "In_progress",
            "Done"
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status phải là Todo, In_progress hoặc Done"
            )

    if "priority" in update_data:

        if update_data["priority"] not in [
            "Low",
            "Medium",
            "High"
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Priority phải là Low, Medium hoặc High"
            )

    if "assignee_id" in update_data:

        new_assignee_id = update_data["assignee_id"]

        # Chỉ Owner được giao / thay đổi người phụ trách
        if member.role != "Owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ Owner mới có quyền giao công việc"
            )

        # Nếu có người được giao mới
        if new_assignee_id is not None:

            assignee = db.query(EventStaff).filter(
                EventStaff.event_id == task.event_id,
                EventStaff.user_id == new_assignee_id
            ).first()

            if assignee is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Người được giao công việc không phải thành viên của sự kiện"
                )

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


@router.delete("/event-tasks/{task_id}",
    response_model=APIResponse
)
def delete_event_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Tìm công việc
    task = db.query(EventTask).filter(
        EventTask.id == task_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy công việc sự kiện"
        )

    # Kiểm tra user có thuộc event không
    member = db.query(EventStaff).filter(
        EventStaff.event_id == task.event_id,
        EventStaff.user_id == current_user.id
    ).first()

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của sự kiện"
        )

    # Chỉ Owner mới được xóa
    if member.role != "Owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Owner của sự kiện mới được xóa công việc"
        )

    db.delete(task)
    db.commit()

    return APIResponse(
        statusCode=200,
        data=None,
        message="Xóa công việc sự kiện thành công",
        timestamp=datetime.now(timezone.utc),
        path=f"/event-tasks/{task_id}",
        error=None
    )