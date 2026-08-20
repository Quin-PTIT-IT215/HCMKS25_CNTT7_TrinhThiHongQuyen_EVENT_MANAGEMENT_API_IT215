from datetime import datetime, timezone
import bcrypt
from app.db.database import SessionLocal
from app.models.user import User
from app.models.event import Event, EventStaff
from app.models.event_task import EventTask


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def seed_data():
    db = SessionLocal()
    try:

        admin = User(
            email="admin@gmail.com",
            password_hash=hash_password("123456"),
            full_name="Admin",
            role="Admin",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )

        user1 = User(
            email="user1@gmail.com",
            password_hash=hash_password("123456"),
            full_name="Nguyễn Văn A",
            role="User",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )

        user2 = User(
            email="user2@gmail.com",
            password_hash=hash_password("123456"),
            full_name="Trần Thị B",
            role="User",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )

        db.add_all([
            admin,
            user1,
            user2
        ])

        db.commit()
        db.refresh(admin)
        db.refresh(user1)
        db.refresh(user2)


        event1 = Event(
            name="Workshop FastAPI",
            description="Workshop học FastAPI",
            owner_id=admin.id,
            created_at=datetime.now(timezone.utc)
        )

        event2 = Event(
            name="Team Building 2026",
            description="Sự kiện team building",
            owner_id=user1.id,
            created_at=datetime.now(timezone.utc)
        )

        db.add_all([
            event1,
            event2
        ])

        db.commit()
        db.refresh(event1)
        db.refresh(event2)


        staff1 = EventStaff(
            event_id=event1.id,
            user_id=admin.id,
            role="Owner",
            joined_at=datetime.now(timezone.utc)
        )

        staff2 = EventStaff(
            event_id=event1.id,
            user_id=user1.id,
            role="Member",
            joined_at=datetime.now(timezone.utc)
        )

        staff3 = EventStaff(
            event_id=event2.id,
            user_id=user1.id,
            role="Owner",
            joined_at=datetime.now(timezone.utc)
        )

        staff4 = EventStaff(
            event_id=event2.id,
            user_id=user2.id,
            role="Member",
            joined_at=datetime.now(timezone.utc)
        )

        db.add_all([
            staff1,
            staff2,
            staff3,
            staff4
        ])

        db.commit()

        task1 = EventTask(
            event_id=event1.id,
            title="Chuẩn bị slide",
            description="Chuẩn bị slide cho workshop",
            assignee_id=user1.id,
            status="Todo",
            priority="High",
            due_date=None,
            created_at=datetime.now(timezone.utc)
        )

        task2 = EventTask(
            event_id=event1.id,
            title="Chuẩn bị phòng",
            description="Kiểm tra phòng tổ chức",
            assignee_id=user1.id,
            status="In_progress",
            priority="Medium",
            due_date=None,
            created_at=datetime.now(timezone.utc)
        )

        task3 = EventTask(
            event_id=event2.id,
            title="Chuẩn bị banner",
            description="Thiết kế banner team building",
            assignee_id=user2.id,
            status="Todo",
            priority="Low",
            due_date=None,
            created_at=datetime.now(timezone.utc)
        )

        db.add_all([
            task1,
            task2,
            task3
        ])

        db.commit()

        print("Seed dữ liệu thành công!")

    except Exception as e:

        db.rollback()

        print("Seed dữ liệu thất bại:")
        print(e)

    finally:

        db.close()


if __name__ == "__main__":
    seed_data()